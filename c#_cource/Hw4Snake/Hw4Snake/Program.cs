using System;

class Program
{
    // Параметры еды
    static int foodX;
    static int foodY;

    // Параметры змейки
    static int head_x = 20;
    static int head_y = 10;
    static int dir = 0;
    static int snakeLen = 10;
    static int[] body_x = new int[100];
    static int[] body_y = new int[100];

    // Рекорд и счет
    static int score = 0;
    static int highScore = 0;

    static void SpawnFood()
    {
        Random rnd = new Random();

        foodX = rnd.Next(0, 119);

        //if (foodX % 2 != 0) foodX += 1;

        foodY = rnd.Next(0, 39);
    }

    static void SetCurrentPosition(string head_print="  ", string food_print = "  ")
    {
        // Тело
        for (int i = 0; i < snakeLen; i++)
        {
            Console.SetCursorPosition(body_x[i], body_y[i]);
            Console.Write(head_print);

        }
        // Голова
        Console.SetCursorPosition(head_x, head_y);
        Console.Write(head_print);

        // Еда
        Console.SetCursorPosition(foodX, foodY);
        Console.Write(food_print);

        // Счет и рекорд
        Console.SetCursorPosition(0, 0);
        Console.Write("Счет: " + score + "  Рекорд: " + highScore + "  ");

    }

    static void ResetGame()
    {
        Console.Clear();

        head_x = 20;
        head_y = 10;
        dir = 0;
        snakeLen = 10;
        score = 0;

        // Сброс позиции змейки
        for (int i = 0; i < snakeLen; i++)
        {
            body_x[i] = head_x - i;
            body_y[i] = 10;
        }

        SpawnFood();
    }

    static void Main(string[] args)
    {
        // Параметры программы
        Console.SetWindowSize(120, 40);
        Console.SetBufferSize(120, 40);
        Console.CursorVisible = false;

        bool isGame = true;
        bool gameRunning = true;

        // Стартовое значение змейки
        for (int i = 0; i < snakeLen; i++)
        {
            body_x[i] = head_x - i;
            body_y[i] = 10;
        }

        // Стартовое значение еды
        SpawnFood();

        while (gameRunning)
        {
            while (isGame)
            {
                // 1. Отчистка
                SetCurrentPosition();

                // 2. Расчет

                // Движение змейки
                if (Console.KeyAvailable == true)
                {
                    ConsoleKeyInfo key;

                    Console.SetCursorPosition(0, 0);
                    key = Console.ReadKey();

                    Console.SetCursorPosition(0, 0);
                    Console.Write("  ");

                    if (key.Key == ConsoleKey.D && dir != 2) dir = 0;
                    if (key.Key == ConsoleKey.S && dir != 3) dir = 1;
                    if (key.Key == ConsoleKey.A && dir != 0) dir = 2;
                    if (key.Key == ConsoleKey.W && dir != 1) dir = 3;
                }

                // Движение головы
                int newHeadX = head_x;
                int newHeadY = head_y;

                if (dir == 0) newHeadX += 1;
                if (dir == 1) newHeadY += 1;
                if (dir == 2) newHeadX -= 1;
                if (dir == 3) newHeadY -= 1;

                // Бессконечное поле
                if (newHeadX < 0) newHeadX = 118;
                if (newHeadX > 118) newHeadX = 0;
                if (newHeadY < 0) newHeadY = 39;
                if (newHeadY > 39) newHeadY = 0;


                // Сдвиг тела
                for (int i = snakeLen; i > 0; i--)
                {
                    body_x[i] = body_x[i - 1];
                    body_y[i] = body_y[i - 1];
                }
                body_x[0] = newHeadX;
                body_y[0] = newHeadY;
                head_x = newHeadX;
                head_y = newHeadY;

                // Проверка на столкновение
                for (int i = 1; i < snakeLen; i++)
                {
                    if (body_x[i] == head_x && body_y[i] == head_y)
                    { 
                        isGame = false;
                        // Обновление рекорда
                        if (score > highScore) highScore = score;
                        break;
                    }
                }


                // Еда
                if (head_x == foodX && head_y == foodY)
                {
                    SpawnFood();
                    snakeLen++;
                    score++;
                }


                // 3. Отрисовка
                SetCurrentPosition("██", "██");

                // 4. Ожидание
                System.Threading.Thread.Sleep(100);

            }
            // Экран проигрыша
            Console.Clear();
            Console.SetCursorPosition(0, 10);
            Console.WriteLine("=====================================");
            Console.WriteLine("        ИГРА ОКОНЧЕНА!");
            Console.WriteLine("=====================================");
            Console.WriteLine($"Ваш счет: {score}");
            Console.WriteLine($"Рекорд:   {highScore}");
            Console.WriteLine("=====================================");
            Console.WriteLine("Нажмите R для перезапуска");
            Console.WriteLine("Нажмите ESC для выхода");
            Console.WriteLine("=====================================");

            ConsoleKeyInfo choice = Console.ReadKey(true);
            if (choice.Key == ConsoleKey.R)
            {
                ResetGame();
                isGame = true;
            }
            else if (choice.Key == ConsoleKey.Escape)
            {
                gameRunning = false;
            }
        }
    }
}
