using UnityEngine;

[RequireComponent(typeof(SteamVR_TrackedController))]
public class TeleportController : MonoBehaviour
{
    public enum TeleportType
    {
        TeleportTypeUseTerrain,
        TeleportTypeUseCollider,
        TeleportTypeUseZeroY
    }

    public bool teleportOnClick = false;
    public TeleportType teleportType = TeleportType.TeleportTypeUseZeroY;

    // The object to teleport (usually the SteamVR_Render's origin)
    public Transform reference
    {
        get
        {
            var top = SteamVR_Render.Top();
            return (top != null) ? top.origin : null;
        }
    }

    private SteamVR_TrackedController trackedController;

    void Start()
    {
        trackedController = GetComponent<SteamVR_TrackedController>();
        if (trackedController == null)
        {
            trackedController = gameObject.AddComponent<SteamVR_TrackedController>();
        }

        trackedController.TriggerClicked += DoClick;

        // Optional: Adjust player's initial height to be on the terrain
        if (teleportType == TeleportType.TeleportTypeUseTerrain)
        {
            var t = reference;
            if (t != null && Terrain.activeTerrain != null)
            {
                float terrainHeight = Terrain.activeTerrain.SampleHeight(t.position);
                t.position = new Vector3(t.position.x, terrainHeight, t.position.z);
            }
        }
    }

    private void OnDestroy()
    {
        if (trackedController != null)
        {
            trackedController.TriggerClicked -= DoClick;
        }
    }

    void DoClick(object sender, ClickedEventArgs e)
    {
        if (!teleportOnClick) return;

        var t = reference;
        if (t == null) return;

        float refY = t.position.y;
        Plane plane = new Plane(Vector3.up, -refY);
        Ray ray = new Ray(this.transform.position, this.transform.forward);

        bool hasGroundTarget = false;
        float dist = 0f;

        if (teleportType == TeleportType.TeleportTypeUseTerrain)
        {
            if (Terrain.activeTerrain != null)
            {
                TerrainCollider tc = Terrain.activeTerrain.GetComponent<TerrainCollider>();
                RaycastHit hitInfo;
                hasGroundTarget = tc.Raycast(ray, out hitInfo, 1000f);
                if(hasGroundTarget) dist = hitInfo.distance;
            }
        }
        else if (teleportType == TeleportType.TeleportTypeUseCollider)
        {
            RaycastHit hitInfo;
            hasGroundTarget = Physics.Raycast(ray, out hitInfo, 1000f);
            if(hasGroundTarget) dist = hitInfo.distance;
        }
        else // TeleportTypeUseZeroY
        {
            hasGroundTarget = plane.Raycast(ray, out dist);
        }

        if (hasGroundTarget)
        {
            Vector3 headPosOnGround = new Vector3(SteamVR_Render.Top().head.localPosition.x, 0.0f, SteamVR_Render.Top().head.localPosition.z);

            // Calculate the destination point
            Vector3 destination = ray.origin + ray.direction * dist;

            // Move the reference object (player rig)
            // The subtraction of head position ensures the player's feet land at the destination, not their head.
            t.position = destination - headPosOnGround;
        }
    }
}