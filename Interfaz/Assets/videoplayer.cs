using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;
using UnityEngine.UI; // Necesario para trabajar con UI

public class VideoAnimation : MonoBehaviour
{
    public VideoPlayer videoPlayer;
    public Button startButton; // Referencia al bot�n de inicio

    void Start()
    {
        // Aseg�rate de que el VideoPlayer est� correctamente asignado
        if (videoPlayer == null)
        {
            Debug.LogError("VideoPlayer no est� asignado.");
            return;
        }

        // Aseg�rate de que el Button est� correctamente asignado
        if (startButton == null)
        {
            Debug.LogError("El bot�n de inicio no est� asignado.");
            return;
        }

        // Asociamos la funci�n que reproduce el video al evento de clic del bot�n
        startButton.onClick.AddListener(StartVideo);
    }

    // Funci�n que inicia la reproducci�n del video cuando se presiona el bot�n
    private void StartVideo()
    {
        videoPlayer.url = "http://127.0.0.1:5000/video";  // URL del video servido desde Flask
        videoPlayer.isLooping = true;  // Si quieres que el video se repita
        videoPlayer.Play();
    }
}

