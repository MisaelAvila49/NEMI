using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AnimationController : MonoBehaviour
{
    private Animator animator;
    private bool isPlaying = false;

    void Start()
    {
        animator = GetComponent<Animator>();

        // Iniciar en pausa
        if (animator != null)
        {
            animator.speed = 0f;
        }
    }

    public void PlayAnimation()
    {
        if (animator != null && !isPlaying)
        {
            animator.speed = 1f; // Reanuda la animación
            isPlaying = true;
        }
    }

    public void PauseAnimation()
    {
        if (animator != null && isPlaying)
        {
            animator.speed = 0f; // Pausa la animación
            isPlaying = false;
        }
    }
}


