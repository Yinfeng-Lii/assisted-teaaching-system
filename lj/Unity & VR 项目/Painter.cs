using UnityEngine;

public class Painter : MonoBehaviour
{
    public Color32 penColor;
    public Transform rayOrigin;
    private RaycastHit hitInfo;
    private bool IsGrabbing;
    private static Board board;

    private void Start()
    {
        foreach (var renderer in GetComponentsInChildren<MeshRenderer>())
        {
            if (renderer.transform == transform)
            {
                continue;
            }
            renderer.material.color = penColor;
        }

        if (!board)
        {
            board = FindObjectOfType<Board>();
        }
    }

    private void Update()
    {
        Ray r = new Ray(rayOrigin.position, rayOrigin.forward);
        if (Physics.Raycast(r, out hitInfo, 0.1f))
        {
            if (hitInfo.collider.tag == "Board")
            {
                board.SetPainterPositon(hitInfo.textureCoord.x, hitInfo.textureCoord.y);
                board.SetPainterColor(penColor);
                board.IsDrawing = true;
                IsGrabbing = true;
            }
        }
        else if (IsGrabbing)
        {
            board.IsDrawing = false;
            IsGrabbing = false;
        }
    }
}