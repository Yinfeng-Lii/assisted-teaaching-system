using UnityEngine;

public class EnvironmentReconstruction : MonoBehaviour
{
    public GameObject[] environmentPrefabs;
    public Vector3[] positions;
    public Vector3[] scales;

    void Start()
    {
        // Instantiate environment objects based on arrays
        if (environmentPrefabs.Length > 0)
        {
            int count = Mathf.Min(environmentPrefabs.Length, positions.Length, scales.Length);
            for (int i = 0; i < count; i++)
            {
                if (environmentPrefabs[i] != null)
                {
                    GameObject environment = Instantiate(environmentPrefabs[i], positions[i], Quaternion.identity);
                    environment.transform.localScale = scales[i];
                }
            }
        }

        // Add lighting setup
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
        RenderSettings.ambientLight = Color.white;

        // Create a default directional light if one doesn't exist
        if (FindObjectOfType<Light>() == null)
        {
            GameObject lightObj = new GameObject("Directional Light");
            Light directionalLight = lightObj.AddComponent<Light>();
            directionalLight.type = LightType.Directional;
            directionalLight.color = Color.white;
            directionalLight.intensity = 1.0f;
            lightObj.transform.rotation = Quaternion.Euler(50, 30, 0);
        }

        // Add shadow setup
        QualitySettings.shadows = ShadowQuality.HardOnly;
        foreach (var renderer in FindObjectsOfType<Renderer>())
        {
            renderer.receiveShadows = true;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.On;
        }
    }
}