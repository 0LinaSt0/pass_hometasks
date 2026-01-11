using System;
using SFML.Learning;
using SFML.Window;

class Program : Game
{
    static string bgTexture = LoadTexture("backgroud.png");
    static string playerTexture = LoadTexture("player.png");
    static string foodTexture = LoadTexture("food.png");

    static string plusOneSound = LoadSound("plus_one.wav");
    static string gameOverSound = LoadSound("game_over.wav");
    static string bgSound = LoadMusic("background.wav");

    static float playerX = 300;
    static float playerY = 220;
    static int playerSize = 56;

    static float playerSpeed = 400;
    static int playerDirection = 1;

    static int playerScore = 0;

    static float foodX;
    static float foodY;
    static int foodSize = 32;

    static void PlayerMove()
    {
        if (GetKey(Keyboard.Key.W) == true) playerDirection = 0;
        if (GetKey(Keyboard.Key.D) == true) playerDirection = 1;
        if (GetKey(Keyboard.Key.S) == true) playerDirection = 2;
        if (GetKey(Keyboard.Key.A) == true) playerDirection = 3;

        if (playerDirection == 0) playerY -= playerSpeed * DeltaTime;
        if (playerDirection == 1) playerX += playerSpeed * DeltaTime;
        if (playerDirection == 2) playerY += playerSpeed * DeltaTime;
        if (playerDirection == 3) playerX -= playerSpeed * DeltaTime;
    }

    static void DrawPlayer()
    {
        if (playerDirection == 0) DrawSprite(playerTexture, playerX, playerY, 64, 64, playerSize, playerSize);
        if (playerDirection == 1) DrawSprite(playerTexture, playerX, playerY, 0, 0, playerSize, playerSize);
        if (playerDirection == 2) DrawSprite(playerTexture, playerX, playerY, 0, 64, playerSize, playerSize);
        if (playerDirection == 3) DrawSprite(playerTexture, playerX, playerY, 64, 0, playerSize, playerSize);
    }
    static void Main(string[] args)
    {
        InitWindow(800, 600, "Meow");

        SetFont("comic.ttf");

        Random rnd = new Random();
        bool isLose = false;

        foodX = rnd.Next(0, 800 - foodSize);
        foodY = rnd.Next(0, 600 - foodSize);

        PlayMusic(bgSound, 20);

        while (true)
        {
            // 1. Расчет
            DispatchEvents();

            if (isLose == false)
            {
                PlayerMove();

                if (playerX + playerSize > foodX && foodX + foodSize > playerX
                && playerY + playerSize > foodY && foodY + foodSize > playerY)
                {
                    foodX = rnd.Next(0, 800 - foodSize);
                    foodY = rnd.Next(0, 600 - foodSize);

                    playerScore += 1;
                    playerSpeed += 10;

                    PlaySound(plusOneSound);
                }

                if (playerX + playerSize > 800 || playerX < 0 || playerY + playerSize > 600 || playerY < 0)
                {
                    isLose = true;
                    PlaySound(gameOverSound);
                }
            }
            else
            {
                if (GetKeyDown(Keyboard.Key.R) == true)
                {
                    isLose = false;
                    playerX = 30;
                    playerY = 220;
                    playerSpeed = 400;
                    playerDirection= 1;
                    playerScore = 0;
                }
            }

            // 2. Отчистка
            ClearWindow();

            // 3. Отрисовка
            DrawSprite(bgTexture, 0, 0);

            SetFillColor(255, 255, 255);
            DrawText(10, 10, "Счёт: " + playerScore.ToString(), 24);

            DrawPlayer();

            DrawSprite(foodTexture, foodX, foodY);

            if (isLose == true)
            {
                //Console.Write("HERE");
                SetFillColor(255, 0, 0);
                DrawText(200, 300, "Упс! Нажми R и начнешь заново", 24);
            }

            DisplayWindow();

            // 4. Ожидание
            Delay(1);
        }
    }
}
