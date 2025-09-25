using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;

public class ShowGraphInUnity : MonoBehaviour
{
    public string url = "http://127.0.0.1:5000/grafica_euler";  // Direcci�n de Flask
    public RawImage displayImage;  // El RawImage donde se mostrar� la gr�fica
    private Texture2D texture;

    public Button startButton; // El bot�n que activar� la carga de la gr�fica

    void Start()
    {
        texture = new Texture2D(600, 400);  // Define el tama�o de la textura
        displayImage.texture = texture;     // Asigna la textura al RawImage
        displayImage.gameObject.SetActive(false);  // Inicialmente ocultamos la gr�fica

        startButton.onClick.AddListener(OnStartButtonPressed);  // Asocia el evento del bot�n
    }

    // Evento que se activa al presionar el bot�n de inicio
    void OnStartButtonPressed()
    {
        displayImage.gameObject.SetActive(true);  // Muestra la gr�fica
        StartCoroutine(UpdateGraph());
    }

    IEnumerator UpdateGraph()
    {
        while (displayImage.gameObject.activeSelf)  // Sigue actualizando solo si est� visible
        {
            // Petici�n para obtener la imagen desde Flask
            UnityWebRequest request = UnityWebRequestTexture.GetTexture(url);
            yield return request.SendWebRequest();  // Espera a la respuesta

            if (request.result == UnityWebRequest.Result.Success)
            {
                // Si la petici�n fue exitosa, obtiene la textura de la imagen
                texture = ((DownloadHandlerTexture)request.downloadHandler).texture;
                displayImage.texture = texture;  // Actualiza el RawImage con la nueva textura
            }
            else
            {
                // Si hubo un error en la solicitud, puedes agregar un mensaje de error aqu�
                Debug.LogError("Error al obtener la gr�fica: " + request.error);
            }

            // Actualiza cada 0.1 segundos
            yield return new WaitForSeconds(0.1f);
        }
    }
}
    