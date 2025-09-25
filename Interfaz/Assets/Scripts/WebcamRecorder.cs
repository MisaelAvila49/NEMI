using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.IO;

public class WebcamRecorder : MonoBehaviour
{
    public RawImage webcamDisplay; // UI element to display the webcam feed
    public Button startButton;     // Button to start recording
    public Button stopButton;      // Button to stop recording
    private WebCamTexture webcamTexture;
    private bool isRecording = false;
    private string tempSaveFolderPath; // Carpeta temporal para guardar durante la ejecución

    void Start()
    {
        // Initialize buttons
        startButton.onClick.AddListener(StartRecording);
        stopButton.onClick.AddListener(StopRecording);

        // Disable stop button initially
        stopButton.interactable = false;

        // Initialize webcam
        webcamTexture = new WebCamTexture(1280, 720, 30); // Especifica resolución y FPS
        webcamDisplay.texture = webcamTexture;
        webcamDisplay.color = Color.white;

        // Start the webcam
        webcamTexture.Play();

        // Set the temporary save folder path
        tempSaveFolderPath = Path.Combine(Application.persistentDataPath, "TempRecordings");
        if (!Directory.Exists(tempSaveFolderPath))
        {
            Directory.CreateDirectory(tempSaveFolderPath);
        }
    }

    void StartRecording()
    {
        isRecording = true;
        startButton.interactable = false;
        stopButton.interactable = true;

        // Limpia la carpeta temporal antes de empezar
        if (Directory.Exists(tempSaveFolderPath))
        {
            Directory.Delete(tempSaveFolderPath, true);
            Directory.CreateDirectory(tempSaveFolderPath);
        }

        // Start capturing frames
        StartCoroutine(CaptureFrames());
    }

    void StopRecording()
    {
        isRecording = false;
        startButton.interactable = true;
        stopButton.interactable = false;

        UnityEngine.Debug.Log("Deteniendo la grabación de frames.");
    }

    IEnumerator CaptureFrames()
    {
        int frameCount = 0;

        while (isRecording)
        {
            // Wait until the end of the frame to capture
            yield return new WaitForEndOfFrame();

            // Capture the current frame
            Texture2D frame = new Texture2D(webcamTexture.width, webcamTexture.height, TextureFormat.RGB24, false);
            frame.SetPixels(webcamTexture.GetPixels());
            frame.Apply();

            // Save the frame as an image in the temporary folder
            byte[] frameData = frame.EncodeToPNG();
            string filePath = Path.Combine(tempSaveFolderPath, $"Frame_{frameCount.ToString("0000")}.png");
            File.WriteAllBytes(filePath, frameData);

            frameCount++;
        }
    }

    void OnDestroy()
    {
        if (webcamTexture != null && webcamTexture.isPlaying)
        {
            webcamTexture.Stop();
        }
    }
}
