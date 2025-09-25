using System.Collections;
using System.Collections.Generic;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections.Generic;

public class SensorDataReceiver : MonoBehaviour
{
    private string serverUrl = "http://127.0.0.1:5000/obtener_datos";

    void Start()
    {
        StartCoroutine(ObtenerDatos());
    }

    IEnumerator ObtenerDatos()
    {
        while (true)
        {
            using (UnityWebRequest request = UnityWebRequest.Get(serverUrl))
            {
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    string json = request.downloadHandler.text;
                    ProcesarDatos(json);
                }
                else
                {
                    Debug.LogError("Error al obtener datos: " + request.error);
                }
            }

            yield return new WaitForSeconds(0.5f);  // Actualizar cada 0.5 segundos
        }
    }

    void ProcesarDatos(string json)
    {
        SensorData[] sensores = JsonHelper.FromJson<SensorData>(json);
        foreach (SensorData sensor in sensores)
        {
            Debug.Log($"📡 Sensor {sensor.sensor_id} - qw: {sensor.qw}, qx: {sensor.qx}, qy: {sensor.qy}, qz: {sensor.qz}");
        }
    }
}

[System.Serializable]
public class SensorData
{
    public string timestamp;
    public int sensor_id;
    public float qw;
    public float qx;
    public float qy;
    public float qz;
}

// Clase auxiliar para deserializar JSON en array
public static class JsonHelper
{
    public static T[] FromJson<T>(string json)
    {
        return JsonUtility.FromJson<Wrapper<T>>(json).items;
    }

    [System.Serializable]
    private class Wrapper<T>
    {
        public T[] items;
    }
}

