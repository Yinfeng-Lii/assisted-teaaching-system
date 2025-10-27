import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

import com.huawei.hms.audioeditor.ui.HAEUIManager;
import com.huawei.hms.audioeditor.sdk.HAEAudioExpansion;
import com.huawei.hms.audioeditor.sdk.HAESpaceRenderFile;
import com.huawei.hms.audioeditor.sdk.HAEAudioSeparationFile;
import com.huawei.hms.audioeditor.sdk.bean.HAEAudioProperty;
import com.huawei.hms.audioeditor.sdk.bean.SeparationBean;
import com.huawei.hms.audioeditor.sdk.bean.SpaceRenderPositionParams;
import com.huawei.hms.audioeditor.sdk.bean.SpaceRenderRotationParams;
import com.huawei.hms.audioeditor.sdk.bean.SpaceRenderExtensionParams;
import com.huawei.hms.audioeditor.sdk.callbacks.AudioExtractCallBack;
import com.huawei.hms.audioeditor.sdk.callbacks.AudioSeparationCallBack;
import com.huawei.hms.audioeditor.sdk.callbacks.OnTransformCallBack;
import com.huawei.hms.audioeditor.sdk.callbacks.SeparationCloudCallBack;
import com.huawei.hms.audioeditor.sdk.constant.HAEConstant;
import com.huawei.hms.audioeditor.sdk.engine.SpaceRenderEngine.SpaceRenderMode;

import java.util.ArrayList;
import java.util.List;

public class AudioEditorActivity extends Activity {
    private static final String TAG = "AudioEditorActivity";
    private Context mContext;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mContext = this;
        // Example usage of the methods below
    }

    // 1. 启动内置的音频编辑器UI
    private void launchEditor() {
        HAEUIManager.getInstance().launchEditorActivity(this);
    }

    // 2. 当作为音频选择器时，返回音频路径给调用方
    private void sendAudioToSdk() {
        // 获取到的音频文件路径 filePath
        String filePath = "/sdcard/AudioEdit/audio/music.aac";
        ArrayList<String> audioList = new ArrayList<>();
        audioList.add(filePath);

        // 将音频文件路径返回到音频编辑页面
        Intent intent = new Intent();
        // 使用 sdk 提供的 HAEConstant.AUDIO_PATH_LIST
        intent.putExtra(HAEConstant.AUDIO_PATH_LIST, audioList);
        // 使用 sdk 提供的 HAEConstant.RESULT_CODE 为结果 CODE
        this.setResult(HAEConstant.RESULT_CODE, intent);
        finish();
    }

    // 3. 音频格式转换 (使用默认输出路径)
    private void transformAudioFormatDefaultPath() {
        String inAudioPath = "/sdcard/input.mp3";
        HAEAudioProperty audioFormat = new HAEAudioProperty(); // Configure format properties here if needed

        HAEAudioExpansion.getInstance().transformAudioUseDefaultPath(mContext, inAudioPath,
            audioFormat, new OnTransformCallBack() {
                @Override
                public void onProgress(int progress) { Log.d(TAG, "Transform Progress: " + progress); }
                @Override
                public void onFail(int errorCode) { Log.e(TAG, "Transform Failed: " + errorCode); }
                @Override
                public void onSuccess(String outPutPath) { Log.d(TAG, "Transform Success: " + outPutPath); }
                @Override
                public void onCancel() { Log.d(TAG, "Transform Canceled"); }
            });
    }

    // 4. 从视频提取音频
    private void extractAudioFromVideo() {
        String inVideoPath = "/sdcard/input.mp4";
        String outAudioDir = "/sdcard/AudioEdit/extracted/"; // 提取出的音频保存的文件夹路径, 非必填
        String outAudioName = "extracted_audio"; // 提取出的音频名称, 不带后缀, 非必填

        HAEAudioExpansion.getInstance().extractAudio(mContext, inVideoPath, outAudioDir,
            outAudioName, new AudioExtractCallBack() {
                @Override
                public void onSuccess(String audioPath) { Log.d(TAG, "ExtractAudio onSuccess : " + audioPath); }
                @Override
                public void onProgress(int progress) { Log.d(TAG, "ExtractAudio onProgress : " + progress); }
                @Override
                public void onFail(int errCode) { Log.i(TAG, "ExtractAudio onFail : " + errCode); }
                @Override
                public void onCancel() { Log.d(TAG, "ExtractAudio onCancel."); }
            });
    }

    // 5. 伴奏分离
    private void separateAudio() {
        HAEAudioSeparationFile haeAudioSeparationFile = new HAEAudioSeparationFile();

        // 5a. 获取可分离的乐器类型ID
        haeAudioSeparationFile.getInstruments(new SeparationCloudCallBack<List<SeparationBean>>() {
            @Override
            public void onFinish(List<SeparationBean> response) {
                Log.d(TAG, "Got instruments: " + response.toString());
                // 假设我们想分离人声，并且从response中得知其ID是"vocals_1"
                startSeparationTask(haeAudioSeparationFile, "vocals_1");
            }
            @Override
            public void onError(int errorCode) { Log.e(TAG, "Failed to get instruments: " + errorCode); }
        });
    }

    private void startSeparationTask(HAEAudioSeparationFile separator, String instrumentId) {
        // 5b. 设置要提取的伴奏参数
        List<String> instruments = new ArrayList<>();
        instruments.add(instrumentId);
        separator.setInstruments(instruments);

        String inAudioPath = "/sdcard/song.mp3";
        String outAudioDir = "/sdcard/separated/";
        String outAudioName = "song_separated";

        // 5c. 开始进行伴奏分离
        separator.startSeparationTasks(inAudioPath, outAudioDir, outAudioName, new AudioSeparationCallBack() {
            @Override
            public void onResult(SeparationBean separationBean) { Log.d(TAG, "Separation partial result: " + separationBean.getSeparationName()); }
            @Override
            public void onFinish(List<SeparationBean> separationBeans) { Log.d(TAG, "Separation finished."); }
            @Override
            public void onFail(int errorCode) { Log.e(TAG, "Separation failed: " + errorCode); }
            @Override
            public void onCancel() { Log.d(TAG, "Separation canceled."); }
        });
    }

    // 6. 空间音频渲染
    private void renderSpatialAudio() {
        String inAudioPath = "/sdcard/sound.wav";
        String outAudioDir = "/sdcard/spatial/";
        String outAudioName = "spatial_sound";
        // ... (需要一个回调对象)

        // 6a. 固定摆位
        HAESpaceRenderFile fixedPositionRenderer = new HAESpaceRenderFile(SpaceRenderMode.POSITION);
        fixedPositionRenderer.setSpacePositionParams(new SpaceRenderPositionParams(1.0f, 0.5f, 0.0f)); // x, y, z
        // fixedPositionRenderer.applyAudioFile(inAudioPath, outAudioDir, outAudioName, callBack);

        // 6b. 动态渲染
        HAESpaceRenderFile dynamicRenderer = new HAESpaceRenderFile(SpaceRenderMode.ROTATION);
        dynamicRenderer.setRotationParams(new SpaceRenderRotationParams(0f, 0f, 0f, 5000, 1)); // x, y, z, surroundTime, surroundDirection
        // dynamicRenderer.applyAudioFile(...);

        // 6c. 扩展模式
        HAESpaceRenderFile extensionRenderer = new HAESpaceRenderFile(SpaceRenderMode.EXTENSION);
        extensionRenderer.setExtensionParams(new SpaceRenderExtensionParams(10.0f, 90.0f)); // radiusVal, angledVal
        // extensionRenderer.applyAudioFile(...);
    }
}