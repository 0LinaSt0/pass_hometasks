using SFML.Graphics;
using SFML.System;
using SFML.Window;
using System;

class Program
{
    static RenderWindow window;

    static Texture ballTexture;
    static Texture stickTexture;
    static Texture blockTexture;

    static Sprite stick;
    static Sprite[] blocks;
    static Ball ball;

    static Font font;
    static Text gameOverText;
    static Text restartText;
    static bool gameOver = false;

    public static void SetStartPosition()
    {
        int idx = 0;

        for (int y = 0; y < 10; y++)
        {
            for (int x = 0; x < 10; x++)
            {
                blocks[idx].Position = new SFML.System.Vector2f(
                    x * (blocks[idx].TextureRect.Width + 15) + 75,
                    y * (blocks[idx].TextureRect.Height + 15) + 50
                );
                idx++;
            }
        }
        stick.Position = new Vector2f(400, 500);
        ball.sprite.Position = new Vector2f(375, 400);
    }

    static void Main(string[] args)
    {
        window = new RenderWindow(new VideoMode(800, 600), "Game");

        font = new Font("comic.ttf");
        // Создание текста Game Over
        gameOverText = new Text("GAME OVER!", font, 48);
        gameOverText.Position = new Vector2f(250, 200);
        gameOverText.FillColor = Color.Red;

        // Текст рестарта
        restartText = new Text("Нажмите R для рестарта", font, 24);
        restartText.Position = new Vector2f(240, 280);
        restartText.FillColor = Color.White;

        window.SetFramerateLimit(60);
        window.Closed += Window_Closed;

        // Load Textures
        ballTexture = new Texture("Ball.png");
        stickTexture = new Texture("Stick.png");
        blockTexture = new Texture("Block.png");

        ball = new Ball(ballTexture);
        stick = new Sprite(stickTexture);
        blocks = new Sprite[100];

        for (int i = 0; i < blocks.Length; i++) blocks[i] = new Sprite(blockTexture);

        SetStartPosition();

        while (window.IsOpen == true)
        {
            window.Clear();
            window.DispatchEvents();

            if (Keyboard.IsKeyPressed(Keyboard.Key.R) && gameOver)
            {
                gameOver = false;
                SetStartPosition();
                ball.Reset(new Vector2f(375, 400));  // Сброс мяча
            }

            if (!gameOver)
            {
                if (Mouse.IsButtonPressed(Mouse.Button.Left))
                {
                    ball.Start(5, new Vector2f(0, -1));
                }
                ball.Move(new Vector2i(0, 0), new Vector2i(800, 600)); 

                ball.CheckCollision(stick, "stick");
                for (int i = 0; i < blocks.Length; i++)
                {
                    if (ball.CheckCollision(blocks[i], "block"))
                    {
                        blocks[i].Position = new Vector2f(1000, 1000);
                        break;
                    }
                }

                // Проверка проигрыша после Move
                if (ball.IsLost)
                {
                    gameOver = true;
                }

                // Движение стика
                stick.Position = new Vector2f(
                    Mouse.GetPosition(window).X - stick.TextureRect.Width * 0.5f,
                    stick.Position.Y
                );
            }

            // Draw

            window.Clear();
            window.Draw(stick);
            window.Draw(ball.sprite);
            for (int i = 0; i < blocks.Length; i++)
            {
                window.Draw(blocks[i]);
            }

            if (gameOver)
            {
                window.Draw(gameOverText);
                window.Draw(restartText);
            }

            window.Display();

        }
    }

    private static void Window_Closed(object sender, EventArgs e)
    {
        window.Close();
    }

}