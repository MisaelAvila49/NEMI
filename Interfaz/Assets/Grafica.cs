using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;

public class ShowGraphInUnity : MonoBehaviour
{
    public string url = "http://127.0.0.1:5000/grafica_euler";  // Dirección de Flask
    public RawImage displayImage;  // El RawImage donde se mostrará la gráfica
    private Texture2D texture;

    public Button startButton; // El botón que activará la carga de la gráfica

    void Start()
    {
        texture = new Texture2D(600, 400);  // Define el tamaño de la textura
        displayImage.texture = texture;     // Asigna la textura al RawImage
        displayImage.gameObject.SetActive(false);  // Inicialmente ocultamos la gráfica

        startButton.onClick.AddListener(OnStartButtonPressed);  // Asocia el evento del botón
    }

    // Evento que se activa al presionar el botón de inicio
    void OnStartButtonPressed()
    {
        displayImage.gameObject.SetActive(true);  // Muestra la gráfica
        StartCoroutine(UpdateGraph());
    }

    IEnumerator UpdateGraph()
    {
        while (displayImage.gameObject.activeSelf)  // Sigue actualizando solo si está visible
        {
            // Petición para obtener la imagen desde Flask
            UnityWebRequest request = UnityWebRequestTexture.GetTexture(url);
            yield return request.SendWebRequest();  // Espera a la respuesta

            if (request.result == UnityWebRequest.Result.Success)
            {
                // Si la petición fue exitosa, obtiene la textura de la imagen
                texture = ((DownloadHandlerTexture)request.downloadHandler).texture;
                displayImage.texture = texture;  // Actualiza el RawImage con la nueva textura
            }
            else
            {
                // Si hubo un error en la solicitud, puedes agregar un mensaje de error aquí
                Debug.LogError("Error al obtener la gráfica: " + request.error);
            }

            // Actualiza cada 0.1 segundos
            yield return new WaitForSeconds(0.1f);
        }
    }
}
    