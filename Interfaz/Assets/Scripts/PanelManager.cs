using UnityEngine;

public class PanelManager : MonoBehaviour
{
    public GameObject panelInicio;  
    public GameObject panelVision;  
    public GameObject panelSimulacion;

    // Método para abrir el panel de inicio
    public void MostrarInicio()
    {
        panelInicio.SetActive(true);   
        panelVision.SetActive(false); 
        panelSimulacion.SetActive(false);
    }

    // Método para abrir el panel de vision
    public void MostrarVision()
    {
        panelInicio.SetActive(false);  
        panelVision.SetActive(true);  
        panelSimulacion.SetActive(false);
    }

    // Método para abrir el panel de simulacion
    public void MostrarSimulacion()
    {
        panelInicio.SetActive(false);
        panelVision.SetActive(false);
        panelSimulacion.SetActive(true);
    }
}