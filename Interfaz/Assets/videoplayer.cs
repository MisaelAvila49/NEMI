using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;
using UnityEngine.UI; // Necesario para trabajar con UI

public class VideoAnimation : MonoBehaviour
{
    public VideoPlayer videoPlayer;
    public Button startButton; // Referencia al botón de inicio

    void Start()
    {
        // Asegúrate de que el VideoPlayer esté correctamente asignado
        if (videoPlayer == null)
        {
            Debug.LogError("VideoPlayer no está asignado.");
            return;
        }

        // Asegúrate de que el Button esté correctamente asignado
        if (startButton == null)
        {
            Debug.LogError("El botón de inicio no está asignado.");
            return;
        }

        // Asociamos la función que reproduce el video al evento de clic del botón
        startButton.onClick.AddListener(StartVideo);
    }

    // Función que inicia la reproducción del video cuando se presiona el botón
    private void StartVideo()
    {
        videoPlayer.url = "http://127.0.0.1:5000/video";  // URL del video servido desde Flask
        videoPlayer.isLooping = true;  // Si quieres que el video se repita
        videoPlayer.Play();
    }
}

