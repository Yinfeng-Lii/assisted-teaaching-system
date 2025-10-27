using System.Linq;
using UnityEngine;

public class Board : MonoBehaviour
{
    [Range(0, 1)]
    public float lerp = 0.05f;
    public Texture2D initailizeTexture;
    private Texture2D currentTexture;
    private Vector2 paintPos;

    private bool isDrawing = false;
    private int lastPaintX;
    private int lastPaintY;
    private int painterTipsWidth = 30;
    private int painterTipsHeight = 15;
    private int textureWidth;
    private int textureHeight;
    private Color32[] painterColor;
    private Color32[] currentColor;
    private Color32[] originColor;

    private void Start()
    {
        Texture2D originTexture = GetComponent<MeshRenderer>().material.mainTexture as Texture2D;
        textureWidth = originTexture.width; // 1920
        textureHeight = originTexture.height; // 1080
        currentTexture = new Texture2D(textureWidth, textureHeight, TextureFormat.RGBA32, false, true);
        currentTexture.SetPixels32(originTexture.GetPixels32());
        currentTexture.Apply();
        GetComponent<MeshRenderer>().material.mainTexture = currentTexture;
        painterColor = Enumerable.Repeat<Color32>(new Color32(255, 0, 0, 255), painterTipsWidth * painterTipsHeight).ToArray<Color32>();
    }

    private void Update()
    {
        // Add your update logic here
    }

    private void OnMouseDown()
    {
        // Add your mouse down logic here
    }

    private void OnMouseDrag()
    {
        // Add your mouse drag logic here
    }

    private void OnMouseUp()
    {
        // Add your mouse up logic here
    }

    private void LateUpdate()
    {
        int texPosX = (int)(paintPos.x * (float)textureWidth - (float)(painterTipsWidth / 2));
        int texPosY = (int)(paintPos.y * (float)textureHeight - (float)(painterTipsHeight / 2));
        if (isDrawing)
        {
            currentTexture.SetPixels32(texPosX, texPosY, painterTipsWidth, painterTipsHeight, painterColor);
            if (lastPaintX != 0 && lastPaintY != 0)
            {
                int lerpCount = (int)(1 / lerp);
                for (int i = 0; i <= lerpCount; i++)
                {
                    int x = (int)Mathf.Lerp((float)lastPaintX, (float)texPosX, lerp * i); // Fixed lerp logic
                    int y = (int)Mathf.Lerp((float)lastPaintY, (float)texPosY, lerp * i); // Fixed lerp logic
                    currentTexture.SetPixels32(x, y, painterTipsWidth, painterTipsHeight, painterColor);
                }
            }
            currentTexture.Apply();
            lastPaintX = texPosX;
            lastPaintY = texPosY;
        }
        else
        {
            lastPaintX = lastPaintY = 0;
        }
    }

    public void SetPainterPositon(float x, float y)
    {
        paintPos.Set(x, y);
    }

    public bool IsDrawing
    {
        get { return isDrawing; }
        set { isDrawing = value; }
    }

    public void SetPainterColor(Color32 color)
    {
        if (!painterColor[0].IsEqual(color))
        {
            for (int i = 0; i < painterColor.Length; i++)
            {
                painterColor[i] = color;
            }
        }
    }
}