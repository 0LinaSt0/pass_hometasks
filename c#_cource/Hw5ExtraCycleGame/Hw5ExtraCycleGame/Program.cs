using System;
using SFML.Learning;
using SFML.Window;
using SFML.System;

class Cycle : Game
{
    static string plusOneSound = LoadSound("plus_one.wav");
    static string gameOverSound = LoadSound("game_over.wav");
    static string bgSound = LoadMusic("background.wav");

    static float outerRadius = 100f;
    static float innerRadius = 0f;

    static float centerX = 400f;
    static float centerY = 300f;

    static float growSpeed = 0.3f;
    static float totalDelta = 0.0f;
    static int clickCount = 0;
    static bool gameOver = false;
    static bool spacePressed = false;

    static float finalScore = 0f;
    static float bestScore = float.MaxValue;
    static bool showNewRecord = false;

    static bool gameOverSoundPlayed = false;


    static void ResetGame()
    {
        outerRadius = 100f;
        innerRadius = 0f;
        totalDelta = 0.0f;
        clickCount = 0;
        gameOver = false;
        finalScore = 0f;       
        showNewRecord = false;
        gameOverSoundPlayed = false;
    }
    static void Update()
    {
        if (GetKey(Keyboard.Key.Space) && !spacePressed && !gameOver)
        {
            PlaySound(plusOneSound);
            spacePressed = true;
            totalDelta += outerRadius - innerRadius;
            clickCount++;

            outerRadius = innerRadius;
            innerRadius = 0f;
        }
        if (!GetKey(Keyboard.Key.Space)) spacePressed = false;

        if (!gameOver)
        {
            innerRadius += growSpeed;

            if (innerRadius > outerRadius)
                gameOver = true;
        }
        else
        {
            if (!gameOverSoundPlayed)
            {
                PlaySound(gameOverSound);
                gameOverSoundPlayed = true;
            }

            if (clickCount > 0 && finalScore == 0f)
            {
                finalScore = totalDelta / clickCount;

                // Проверка и обновление рекорда
                if ((float)Math.Round(finalScore, 1) < (float)Math.Round(bestScore, 1))
                {
                    bestScore = finalScore;
                    showNewRecord = true;
                }
            }
            // перезапуск после проигрыша
            if (GetKeyDown(Keyboard.Key.R)) ResetGame();
        }
    }

    static void Draw()
    {
        // внешний круг
        FillCircle(centerX, centerY, outerRadius + 3);
        SetFillColor(0, 0, 0);
        FillCircle(centerX, centerY, outerRadius);

        // внутренний круг
        if (!gameOver)
        {
            SetFillColor(255, 0, 0);
            FillCircle(centerX, centerY, innerRadius);
        }

        // текст
        SetFillColor(255, 255, 255);
        DrawText(10, 10, "ИНСТРУКЦИЯ: Твоя задача - остановить рост (SPACE) внутреннего круга не заходя за пределы внешнего.");
        DrawText(10, 30, "При этом твой круг должен быть максимально близок ко внешнему.");
        DrawText(10, 50, "Расстояние между кругами замеряется на каждой итерации.");
        DrawText(10, 70, "Игра закончится как только твой внутренний круг выйдет за пределы внешнего.");
        DrawText(10, 90, "Чем меньше средняя разница между твоим и внешним кругом по итогу игры, тем лучше. Удачи!");
        DrawText(10, 110, "Внешний: " + ((int)outerRadius).ToString(), 16);
        DrawText(10, 130, "Внутренний: " + ((int)innerRadius).ToString(), 16);
        DrawText(10, 150, "Кликов: " + clickCount.ToString(), 16);
        DrawText(10, 170, "Рекорд: " + (bestScore == float.MaxValue ? "-" : bestScore.ToString("F1")), 16);


        if (gameOver && clickCount > 0)
        {
            ClearWindow();
            SetFillColor(255, 255, 255);

            DrawText(250, 250, "GAME OVER", 32);
            DrawText(270, 290, "Результат: " + finalScore.ToString("F1"), 20);
            DrawText(270, 320, "Текущий рекорд: " + bestScore.ToString("F1"), 20);

            if (showNewRecord)
                DrawText(270, 350, "Ты поставил рекорд!", 20);
            else
                DrawText(270, 350, "Меньше = лучше!", 18);

            DrawText(250, 390, "R для перезапуска", 18);
        }
    }

    static void Main()
    {
        InitWindow(800, 600, "Cycle");
        SetFont("comic.ttf");

        PlayMusic(bgSound, 20);

        while (true)
        {
            DispatchEvents();
            Update();
            ClearWindow();
            Draw();
            DisplayWindow();
            Delay(1);
        }
    }
}
