using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.Collections;

public class GraphUpdater : MonoBehaviour
{
    public RawImage rawImage;  // Arrastra tu RawImage aquí en el Inspector

    private string url = "http://127.0.0.1:5000/grafica_euler";  // URL de tu servidor Flask

    // Llama este método para actualizar la gráfica

    public void ActualizarGrafica()
    {
        StartCoroutine(CargarGrafica());
    }

    private IEnumerator CargarGrafica()
    {
        using (UnityWebRequest webRequest = UnityWebRequestTexture.GetTexture(url))
        {
            // Enviar la solicitud GET para obtener la imagen
            yield return webRequest.SendWebRequest();

            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                // Obtener la textura desde la respuesta
                Texture2D texture = ((DownloadHandlerTexture)webRequest.downloadHandler).texture;

                // Asignar la textura a la RawImage
                rawImage.texture = texture;
            }
            else
            {
                Debug.LogError("Error al cargar la gráfica: " + webRequest.error);
            }
        }
    }
}

