import torch
import torch.nn as nn
from torch.nn.functional import grid_sample

# Assuming PointTensor and SPVCNN are defined in another file from a sparse convolution library
# like MinkowskiEngine or spconv. For demonstration, we'll create dummy classes.
class PointTensor:
    def __init__(self, features, coords):
        self.features = features
        self.coords = coords

class SPVCNN(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        # Placeholder for a sparse conv network
        self.net = nn.Identity()
    def forward(self, x):
        return x.features
        
class GRUFusion(nn.Module):
    def __init__(self, cfg, channels):
        super().__init__()
        # Placeholder for GRU Fusion module
        self.net = nn.Identity()
    def forward(self, up_coords, feat, tsdf_target, occ_target):
        return up_coords, feat, tsdf_target, occ_target


def generate_grid(n_vox, interval):
    with torch.no_grad():
        # Create voxel grid
        grid_range = [torch.arange(0, n_vox[axis] * interval, interval) for axis in range(3)]
        grid = torch.stack(torch.meshgrid(grid_range[0], grid_range[1], grid_range[2], indexing='ij')) # 3 dx dy dz
        grid = grid.unsqueeze(0).cuda().float() # 1 3 dx dy dz
        grid = grid.view(1, 3, -1)
        return grid

def back_project(coords, origin, voxel_size, feats, KRcam):
    """
    Unproject the image fetures to form a 3D (sparse) feature volume
    :param coords: coordinates of voxels, dim: (num of voxels, 4) (4: batch ind, x, y, z)
    :param origin: origin of the partial voxel volume, dim: (batch size, 3) (3: x, y, z)
    :param voxel_size: floats specifying the size of a voxel
    :param feats: image features, dim: (num of views, batch size, C, H, W)
    :param KRcam: projection matrix, dim: (num of views, batch size, 4, 4)
    :return: feature_volume_all: 3D feature volumes, dim: (num of voxels, c + 1)
    :return: count: number of times each voxel can be seen, dim: (num of voxels,)
    """
    n_views, bs, c, h, w = feats.shape

    #体素特征初始化,c+1 表示有c个特征是从图像中获取,还有1个特征深度特征
    feature_volume_all = torch.zeros(coords.shape[0], c + 1).cuda()
    count = torch.zeros(coords.shape[0]).cuda()

    for batch in range(bs):
        #找到当前 batch对应的片段
        batch_ind = torch.nonzero(coords[:, 0] == batch).squeeze(1)
        if len(batch_ind) == 0: continue
        coords_batch = coords[batch_ind][:, 1:]

        coords_batch = coords_batch.view(-1, 3)
        origin_batch = origin[batch].unsqueeze(0)
        feats_batch = feats[:, batch]
        #相机内外参
        proj_batch = KRcam[:, batch]

        #体素索引*体素大小+初始位置得到体素的实际位置
        grid_batch = coords_batch * voxel_size + origin_batch.float()
        # 初始化一个[n_views,3,体素个数]的坐标矩阵
        rs_grid = grid_batch.unsqueeze(0).expand(n_views, -1, -1)
        rs_grid = rs_grid.permute(0, 2, 1).contiguous()
        nV = rs_grid.shape[-1]

        # 将矩阵再拼接一个全为1的维度,变为4个维度,以方便进行坐标变换
        rs_grid = torch.cat([rs_grid, torch.ones([n_views, 1, nV]).cuda()], dim=1)

        # Project grid
        #进行坐标映射得到像素坐标
        im_p = proj_batch @ rs_grid
        im_x, im_y, im_z = im_p[:, 0], im_p[:, 1], im_p[:, 2]
        im_x = im_x / (im_z + 1e-8)
        im_y = im_y / (im_z + 1e-8)

        #mask 操作,转化为像素坐标后可能会出现越界,mask 掉
        im_grid = torch.stack([2 * im_x / (w - 1) - 1, 2 * im_y / (h - 1) - 1], dim=-1)
        mask = (im_grid.abs() <= 1).all(dim=-1) & (im_z > 0)

        #特征图
        feats_batch = feats_batch.view(n_views, c, h, w)
        #每个体素的映射坐标
        im_grid = im_grid.view(n_views, 1, -1, 2)
        
        #通过周围四个点插值得到对应的特征
        features = grid_sample(feats_batch, im_grid, padding_mode='zeros', align_corners=True)

        #去掉越界和 nan 值
        features = features.view(n_views, c, -1)
        mask = mask.view(n_views, -1)
        im_z = im_z.view(n_views, -1)
        # remove nan
        features[~mask.unsqueeze(1).expand(-1, c, -1)] = 0
        im_z[~mask] = 0

        count[batch_ind] = mask.sum(dim=0).float()

        # aggregate multi view (求平均)
        features = features.sum(dim=0)
        mask_sum = mask.sum(dim=0)
        invalid_mask = mask_sum == 0
        mask_sum[invalid_mask] = 1
        in_scope_mask = mask_sum.unsqueeze(0)
        features /= in_scope_mask
        features = features.permute(1, 0).contiguous()

        # concat normalized depth value
        #第81个维度的信息就是z,即深度信息,进行标准化
        im_z = im_z.sum(dim=0).unsqueeze(1) / in_scope_mask.permute(1, 0).contiguous()
        
        im_z_mean = im_z[im_z > 0].mean() if (im_z > 0).any() else torch.tensor(0.0).cuda()
        im_z_std = torch.norm(im_z[im_z > 0] - im_z_mean) + 1e-5
        im_z_norm = (im_z - im_z_mean) / im_z_std
        im_z_norm[im_z <= 0] = 0
        
        features = torch.cat([features, im_z_norm], dim=1)
        feature_volume_all[batch_ind] = features
        
    return feature_volume_all, count


class NeuConNet(nn.Module):
    """Coarse-to-fine network."""
    def __init__(self, cfg):
        super(NeuConNet, self).__init__()
        self.cfg = cfg
        self.n_scales = len(cfg.THRESHOLDS) - 1
        alpha = int(self.cfg.BACKBONE2D.ARC.split('-')[-1])
        ch_in = [80 * alpha + 1, 96 + 40 * alpha + 2 + 1, 48 + 24 * alpha + 2 + 1, 24 + 24 + 2 + 1]
        channels = [96, 48, 24]
        
        self.sp_convs = nn.ModuleList()
        self.tsdf_preds = nn.ModuleList()
        self.occ_preds = nn.ModuleList()
        
        if self.cfg.FUSION.FUSION_ON:
            self.gru_fusion = GRUFusion(cfg, channels)
            
        for i in range(len(cfg.THRESHOLDS)):
            self.sp_convs.append(
                SPVCNN(num_classes=1, in_channels=ch_in[i],
                       pres=1,
                       cr=1 / 2 ** i,
                       vres=self.cfg.VOXEL_SIZE * 2 ** (self.n_scales - i),
                       dropout=self.cfg.SPARSEREG.DROPOUT)
            )
            if i > 0:
                self.tsdf_preds.append(nn.Linear(channels[i-1], 1))
                self.occ_preds.append(nn.Linear(channels[i-1], 1))

    def get_target(self, coords, inputs, scale):
        # ... (Implementation from page 19)
        pass

    def upsample(self, pre_feat, pre_coords, interval, num=8):
        # ... (Implementation from page 19)
        pass
        
    def forward(self, features, inputs, outputs):
        bs = features[0][0].shape[0]
        pre_feat = None
        pre_coords = None
        loss_dict = {}

        # ----coarse to fine----
        for i in range(self.cfg.N_LAYER):
            interval = 2 ** (self.n_scales - i)
            scale = self.n_scales - i

            if i == 0:
                # ----generate new coords----
                coords = generate_grid(self.cfg.N_VOX, interval)[0]
                up_coords = []
                for b in range(bs):
                    up_coords.append(torch.cat([torch.ones(1, coords.shape[-1]).to(coords.device) * b, coords]))
                up_coords = torch.cat(up_coords, dim=1).permute(1, 0).contiguous()
            else:
                # ----upsample coords----
                up_feat, up_coords = self.upsample(pre_feat, pre_coords, interval)
            
            # ----back project----
            feats = torch.stack([feat[scale] for feat in features])
            KRcam = inputs['proj_matrices'][:, :, scale].permute(1, 0, 2, 3).contiguous()
            volume, count = back_project(up_coords, inputs['vol_origin_partial'], self.cfg.VOXEL_SIZE, feats, KRcam)

            grid_mask = count > 1
            
            # ----concat feature from last stage----
            if i != 0:
                feat = torch.cat([volume, up_feat], dim=1)
            else:
                feat = volume
            
            # ... (rest of the logic from pages 21-22 for sparse conv, loss, etc.)
            
        return outputs, loss_dict