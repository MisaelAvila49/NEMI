using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class Conectar_sensores : MonoBehaviour
{
    private string url = "http://127.0.0.1:5000/conectar_sensores"; 

    public void Conectar()
    {
        StartCoroutine(EnviarSolicitud());
    }

    IEnumerator EnviarSolicitud()
    {
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm(url, ""))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("✅ Sensores conectados: " + request.downloadHandler.text);
            }
            else
            {
                Debug.LogError("❌ Error al conectar sensores: " + request.error);
            }
        }
    }
}
