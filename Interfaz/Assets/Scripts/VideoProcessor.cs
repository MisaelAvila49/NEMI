using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.IO;
using System.Collections;
using System.Text;
using UnityEngine.Video; // Agregar este namespace

public class VideoProcessor : MonoBehaviour
{
    [Header("UI Elements")]
    public Button sendButton;
    
    public VideoPlayer videoPlayer; // Agregar referencia al VideoPlayer
    public RawImage videoDisplay; // UI element para mostrar el video

    [Header("API Configuration")]
    public string apiUrl = "http://localhost:8000/procesar_grabacion/";
    public string downloadVideoUrl = "http://localhost:8000/descargar_video/";
    public string downloadCsvUrl = "http://localhost:8000/descargar_csv/";
    public int targetFPS;

    [Header("Paths")]
    private string framesFolderName = "TempRecordings";
    private string videosFolderName = "ProcessedVideos";

    private string framesDirectory;
    private string videosDirectory;
    private string sessionId;
    private bool isProcessing = false;

    void Start()
    {
        framesDirectory = Path.Combine(Application.persistentDataPath, framesFolderName);
        videosDirectory = Path.Combine(Application.persistentDataPath, videosFolderName);
        
        // Crear directorio para videos si no existe
        if (!Directory.Exists(videosDirectory))
        {
            Directory.CreateDirectory(videosDirectory);
        }

        Debug.Log($"Buscando frames en: {framesDirectory}");
        Debug.Log($"Frames encontrados: {Directory.GetFiles(framesDirectory, "*.png").Length}");
        
        sendButton.onClick.AddListener(OnSendButtonClick);
        UpdateButtonState();

        // Configurar VideoPlayer
        videoPlayer.playOnAwake = false;
        videoPlayer.isLooping = true;
        videoPlayer.renderMode = VideoRenderMode.RenderTexture;
        videoPlayer.targetTexture = new RenderTexture((int)videoDisplay.rectTransform.rect.width, 
                                                    (int)videoDisplay.rectTransform.rect.height, 24);
        videoDisplay.texture = videoPlayer.targetTexture;
    }

    void UpdateButtonState()
    {
        sendButton.interactable = !isProcessing && Directory.Exists(framesDirectory) && 
                                Directory.GetFiles(framesDirectory, "*.png").Length > 0;
    }

    public void OnSendButtonClick()
    {
        if (!isProcessing)
        {
            StartCoroutine(SendFramesToAPI());
        }
    }

    IEnumerator SendFramesToAPI()
    {
        isProcessing = true;
        UpdateButtonState();

        // Verificar que existen frames
        string[] frameFiles = Directory.GetFiles(framesDirectory, "*.png");
        if (frameFiles.Length == 0)
        {
            Debug.LogError("No frames found in directory: " + framesDirectory);
            isProcessing = false;
            UpdateButtonState();
            yield break;
        }

        // Crear objeto de request
        var requestData = new ProcessRequestData
        {
            frames_dir = framesDirectory,
            fps = targetFPS
        };

        string jsonData = JsonUtility.ToJson(requestData);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);

        using (UnityWebRequest request = new UnityWebRequest(apiUrl, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"API Error: {request.error}\nResponse: {request.downloadHandler.text}");
            }
            else
            {
                // Procesar respuesta
                var response = JsonUtility.FromJson<ApiResponse>(request.downloadHandler.text);
                sessionId = response.session_id;
                Debug.Log($"Successfully processed {response.frames_processed} frames. Session ID: {sessionId}");
                
                // Descargar y reproducir el video procesado
                yield return StartCoroutine(DownloadAndPlayVideo(sessionId));
            }
        }

        isProcessing = false;
        UpdateButtonState();
    }

    IEnumerator DownloadAndPlayVideo(string sessionId)
    {
        string videoUrl = $"{downloadVideoUrl}{sessionId}";
        string csvUrl = $"{downloadCsvUrl}{sessionId}";
        // Cambiar la ruta a la carpeta Videos del usuario
        string videosPath = Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.MyVideos), "Nemi");

        // Crear la carpeta si no existe
        if (!Directory.Exists(videosPath))
        {
            Directory.CreateDirectory(videosPath);
        }

        string localVideoPath = Path.Combine(videosPath, $"processed_{sessionId}.mp4");

        using (UnityWebRequest request = UnityWebRequest.Get(videoUrl))
        {
            request.downloadHandler = new DownloadHandlerFile(localVideoPath);
            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"Error downloading video: {request.error}");
            }
            else
            {
                Debug.Log($"Video downloaded to: {localVideoPath}");

                // Configurar y reproducir el video
                videoPlayer.source = VideoSource.Url;
                videoPlayer.url = localVideoPath;
                videoPlayer.Prepare();

                while (!videoPlayer.isPrepared)
                {
                    yield return null;
                }

                videoPlayer.Play();
                Debug.Log("Playing processed video");
            }
        }
        
        string localCsvPath = Path.Combine(videosPath, $"analysis_{sessionId}.csv");

        using (UnityWebRequest request = UnityWebRequest.Get(csvUrl))
        {
            request.downloadHandler = new DownloadHandlerFile(localCsvPath);
            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"Error downloading csv: {request.error}");
            }
            else
            {
                Debug.Log($"Csv downloaded to: {localCsvPath}");

            }
        }
}

    // Clases para serialización JSON
    [System.Serializable]
    private class ProcessRequestData
    {
        public string frames_dir;
        public int fps;
    }

    [System.Serializable]
    private class ApiResponse
    {
        public string session_id;
        public string message;
        public int frames_processed;
        public float duration_seconds;
    }

    // Método para verificar frames disponibles
    public int GetAvailableFrameCount()
    {
        if (Directory.Exists(framesDirectory))
        {
            return Directory.GetFiles(framesDirectory, "*.png").Length;
        }
        return 0;
    }

    // Método para mostrar preview del primer frame
    public void ShowFirstFramePreview()
    {
        string[] frameFiles = Directory.GetFiles(framesDirectory, "*.png");
        if (frameFiles.Length > 0)
        {
            byte[] fileData = File.ReadAllBytes(frameFiles[0]);
            Texture2D tex = new Texture2D(2, 2);
            tex.LoadImage(fileData);
        }
    }
}