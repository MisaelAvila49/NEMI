using UnityEngine;
using System.Collections.Generic;
using System.IO;

public class CSV : MonoBehaviour
{
    public TextAsset csvFile;
    public float playbackSpeed = 1.0f;

    // Referencias a los huesos
    public Transform hips;
    public Transform thighL;
    public Transform shinL;
    public Transform footL;
    public Transform thighR;
    public Transform shinR;
    public Transform footR;

    private List<AnimationFrame> animationFrames = new List<AnimationFrame>();
    private int currentFrame = 0;
    private float frameTimer = 0f;
    private bool isPlaying = false;

    private class AnimationFrame
    {
        public float time;
        public Vector3 hipsPosition;
        public Quaternion hipsRotation;
        public Quaternion thighLRotation;
        public Quaternion shinLRotation;
        public Quaternion footLRotation;
        public Quaternion thighRRotation;
        public Quaternion shinRRotation;
        public Quaternion footRRotation;
    }

    void Start()
    {
        LoadAnimationData();
        if (animationFrames.Count > 0)
        {
            isPlaying = true;
            ApplyFrame(animationFrames[0]);
        }
    }

    void Update()
    {
        if (!isPlaying || animationFrames.Count == 0) return;

        frameTimer += Time.deltaTime * playbackSpeed;
        float frameTime = 1f / 60f;

        if (frameTimer >= frameTime)
        {
            frameTimer = 0f;
            currentFrame = (currentFrame + 1) % animationFrames.Count;
            ApplyFrame(animationFrames[currentFrame]);
        }
    }

    void LoadAnimationData()
    {
        if (csvFile == null)
        {
            Debug.LogError("No CSV file assigned");
            return;
        }

        string[] lines = csvFile.text.Split('\n');

        for (int i = 1; i < lines.Length; i++)
        {
            if (string.IsNullOrEmpty(lines[i])) continue;

            string[] values = lines[i].Split(',');

            if (values.Length < 32) continue;

            AnimationFrame frame = new AnimationFrame();
            frame.time = float.Parse(values[0]);

            frame.hipsPosition = new Vector3(
                float.Parse(values[1]),
                float.Parse(values[2]),
                float.Parse(values[3]));

            frame.hipsRotation = new Quaternion(
                float.Parse(values[4]),
                float.Parse(values[5]),
                float.Parse(values[6]),
                float.Parse(values[7]));

            frame.thighLRotation = new Quaternion(
                float.Parse(values[8]),
                float.Parse(values[9]),
                float.Parse(values[10]),
                float.Parse(values[11]));

            frame.shinLRotation = new Quaternion(
                float.Parse(values[12]),
                float.Parse(values[13]),
                float.Parse(values[14]),
                float.Parse(values[15]));

            frame.footLRotation = new Quaternion(
                float.Parse(values[16]),
                float.Parse(values[17]),
                float.Parse(values[18]),
                float.Parse(values[19]));

            frame.thighRRotation = new Quaternion(
                float.Parse(values[20]),
                float.Parse(values[21]),
                float.Parse(values[22]),
                float.Parse(values[23]));

            frame.shinRRotation = new Quaternion(
                float.Parse(values[24]),
                float.Parse(values[25]),
                float.Parse(values[26]),
                float.Parse(values[27]));

            frame.footRRotation = new Quaternion(
                float.Parse(values[28]),
                float.Parse(values[29]),
                float.Parse(values[30]),
                float.Parse(values[31]));

            animationFrames.Add(frame);
        }
    }

    void ApplyFrame(AnimationFrame frame)
    {
        if (hips != null)
        {
            hips.localPosition = frame.hipsPosition;
            hips.localRotation = frame.hipsRotation;
        }

        if (thighL != null) thighL.localRotation = frame.thighLRotation;
        if (shinL != null) shinL.localRotation = frame.shinLRotation;
        if (footL != null) footL.localRotation = frame.footLRotation;

        if (thighR != null) thighR.localRotation = frame.thighRRotation;
        if (shinR != null) shinR.localRotation = frame.shinRRotation;
        if (footR != null) footR.localRotation = frame.footRRotation;
    }
}