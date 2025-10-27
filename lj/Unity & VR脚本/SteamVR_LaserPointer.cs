using UnityEngine;

public class SteamVR_LaserPointer : MonoBehaviour
{
    public bool active = true;
    public Color color = Color.red;
    public float thickness = 0.002f;
    public GameObject holder;
    public GameObject pointer;
    public bool addRigidBody = false;
    
    public event PointerEventHandler PointerIn;
    public event PointerEventHandler PointerOut;

    private bool isActive = false;
    private Transform previousContact = null;
    private SteamVR_TrackedController controller;

    void Start()
    {
        // Get the tracked controller script
        controller = GetComponent<SteamVR_TrackedController>();

        // Holder for the laser pointer visuals
        holder = new GameObject("LaserPointerHolder");
        holder.transform.parent = this.transform;
        holder.transform.localPosition = Vector3.zero;
        holder.transform.localRotation = Quaternion.identity;

        // Create the laser beam (pointer)
        pointer = GameObject.CreatePrimitive(PrimitiveType.Cube);
        pointer.transform.parent = holder.transform;
        pointer.transform.localScale = new Vector3(thickness, thickness, 100f);
        pointer.transform.localPosition = new Vector3(0f, 0f, 50f);
        pointer.transform.localRotation = Quaternion.identity;

        // Handle collider and rigidbody
        BoxCollider colliderComponent = pointer.GetComponent<BoxCollider>();
        if (addRigidBody)
        {
            if (colliderComponent)
            {
                colliderComponent.isTrigger = true;
            }
            Rigidbody rigidBody = pointer.AddComponent<Rigidbody>();
            rigidBody.isKinematic = true;
        }
        else
        {
            Object.Destroy(colliderComponent);
        }

        // Set material and color
        Material newMaterial = new Material(Shader.Find("Unlit/Color"));
        newMaterial.SetColor("_Color", color);
        pointer.GetComponent<MeshRenderer>().material = newMaterial;
    }

    void Update()
    {
        if (!isActive)
        {
            isActive = true;
            this.transform.GetChild(0).gameObject.SetActive(true);
        }

        float dist = 100f;

        Ray raycast = new Ray(transform.position, transform.forward);
        RaycastHit hit;
        bool bHit = Physics.Raycast(raycast, out hit);

        // Check if the hit target has changed
        if (previousContact && previousContact != hit.transform)
        {
            PointerEventArgs args = new PointerEventArgs();
            if (controller != null) args.controllerIndex = controller.controllerIndex;
            args.distance = 0f;
            args.flags = 0;
            args.target = previousContact;
            OnPointerOut(args);
            previousContact = null;
        }

        if (bHit && previousContact != hit.transform)
        {
            PointerEventArgs argsIn = new PointerEventArgs();
            if (controller != null) argsIn.controllerIndex = controller.controllerIndex;
            argsIn.distance = hit.distance;
            argsIn.flags = 0;
            argsIn.target = hit.transform;
            OnPointerIn(argsIn);
            previousContact = hit.transform;
        }

        if (!bHit)
        {
            previousContact = null;
        }

        if (bHit && hit.distance < 100f)
        {
            dist = hit.distance;
        }

        // Handle trigger press for visual feedback
        if (controller != null && controller.triggerPressed)
        {
            pointer.transform.localScale = new Vector3(thickness * 5f, thickness * 5f, dist);
        }
        else
        {
            pointer.transform.localScale = new Vector3(thickness, thickness, dist);
        }
        pointer.transform.localPosition = new Vector3(0f, 0f, dist / 2f);
    }

    public virtual void OnPointerIn(PointerEventArgs e)
    {
        PointerIn?.Invoke(this, e);
    }

    public virtual void OnPointerOut(PointerEventArgs e)
    {
        PointerOut?.Invoke(this, e);
    }
}