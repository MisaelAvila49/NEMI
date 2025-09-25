using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;

public class GraficarEuler : MonoBehaviour
{
    public LineRenderer linePhi;
    public LineRenderer lineTheta;
    public LineRenderer linePsi;
    private List<Vector3> puntosPhi = new List<Vector3>();
    private List<Vector3> puntosTheta = new List<Vector3>();
    private List<Vector3> puntosPsi = new List<Vector3>();

    private string url = "";

    void Start()
    {
        // Configuración básica de los LineRenderers
        ConfigurarLineRenderer(linePhi, Color.blue);
        ConfigurarLineRenderer(lineTheta, Color.green);
        ConfigurarLineRenderer(linePsi, Color.red);

        // Comienza la actualización de la gráfica cada segundo
        StartCoroutine(ActualizarGrafica());
    }

    // Método auxiliar para configurar un LineRenderer
    void ConfigurarLineRenderer(LineRenderer line, Color color)
    {
        line.startWidth = 0.05f;  // Grosor al inicio de la línea
        line.endWidth = 0.05f;    // Grosor al final de la línea

        line.startColor = color;  // Color al inicio de la línea
        line.endColor = color;    // Color al final de la línea

        line.material = new Material(Shader.Find("Unlit/Color")); // Material sin iluminación


    }

    IEnumerator ActualizarGrafica()
    {
        while (true)
        {
            UnityWebRequest request = UnityWebRequest.Get(url);
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string jsonData = request.downloadHandler.text;
                DatosSensores datos = JsonUtility.FromJson<DatosSensores>("{\"datos\":" + jsonData + "}");

                if (datos.datos.Count > 0)
                {
                    puntosPhi.Clear();
                    puntosTheta.Clear();
                    puntosPsi.Clear();

                    for (int i = 0; i < datos.datos.Count; i++)
                    {
                        float x = datos.datos[i].timestamp;
                        float phi = datos.datos[i].phi;
                        float theta = datos.datos[i].theta;
                        float psi = datos.datos[i].psi;

                        puntosPhi.Add(new Vector3(x, phi, 0));
                        puntosTheta.Add(new Vector3(x, theta, 0));
                        puntosPsi.Add(new Vector3(x, psi, 0));
                    }

                    ActualizarLineRenderer(linePhi, puntosPhi);
                    ActualizarLineRenderer(lineTheta, puntosTheta);
                    ActualizarLineRenderer(linePsi, puntosPsi);
                }
            }
            yield return new WaitForSeconds(1f);
        }
    }

    void ActualizarLineRenderer(LineRenderer line, List<Vector3> puntos)
    {
        line.positionCount = puntos.Count;
        line.SetPositions(puntos.ToArray());
    }
}

[System.Serializable]
public class DatosSensores
{
    public List<DatoSensor> datos;
}

[System.Serializable]
public class DatoSensor
{
    public float timestamp;
    public float phi;
    public float theta;
    public float psi;
}
