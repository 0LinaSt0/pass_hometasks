class Program
{
    static void Main()
    {
        Random rnd = new Random();

        // define variables
        int playerHealth = 100;
        int playerEnergy = 100;

        int enemyHealth = 100;
        int enemyEnergy = 100;

        int action = -1;

        while (true)
        {
            // Show skills statuses
            Console.Clear();

            Console.WriteLine("    Жизни: {0}         Жизни вируса:{1}", playerHealth, enemyHealth);
            Console.WriteLine("    Энергия: {0}       Энергия вируса:{1}", playerEnergy, enemyEnergy);

            Console.WriteLine();

            Console.WriteLine("1. Почистить папку Temp (20 урон , -10 энергии) ");
            Console.WriteLine("2. Использовать Касперского (30 урон, -40 энергии) ");
            Console.WriteLine("3. Выпить кофе (+20 энергии) ");
            Console.WriteLine("4. Заказать доставку пиццы (+30 жизни, -20 энергии) ");

            Console.WriteLine();

            // Show win or faight
            if (playerHealth <= 0 || playerEnergy < 0)
            {
                Console.WriteLine("Вирус выиграл!");
                break;
            }

            if (enemyHealth <= 0)
            {
                Console.WriteLine("Ты выиграл!");
                break;
            }

            // Get action
            action = int.Parse(Console.ReadLine());

            // Action logic
            if (action == 1)
            {
                if (playerEnergy >= 10)
                {
                    enemyHealth -= 20;
                    playerEnergy -= 10;
                    Console.WriteLine("Ты потерял 10 энергии и нанес 20 урона");
                }
                else
                {
                    Console.WriteLine("Не достаточно энергии. Ты пропустил этот ход!");
                }
                Console.ReadLine();
            }

            if (action == 2)
            {
                if (playerEnergy >= 40)
                {
                    enemyHealth -= 30;
                    playerEnergy -= 40;
                    Console.WriteLine("Ты потерял 40 энергии и нанес 30 урона");
                }
                else
                {
                    Console.WriteLine("Не достаточно энергии. Ты пропустил этот ход!");
                }
                Console.ReadLine();
            }
            if (action == 3)
            {
                if (playerEnergy < 80)
                {
                    playerEnergy += 20;
                    Console.WriteLine("Ты восстановил 20 энергии");
                }
                else
                {
                    Console.WriteLine("Куда тебе? Все нормально у тебя энергией. Ты пропустил этот ход!");
                }
                    
                Console.ReadLine();
            }
            if (action == 4)
            {
                if (playerEnergy >= 20 && playerHealth <= 70)
                {
                    playerHealth += 30;
                    playerEnergy -= 20;
                    Console.WriteLine("Ты потерял 20 энергии и восстановил 30 здоровья");
                }
                if (playerHealth > 70)
                {
                    Console.WriteLine("Куда тебе? Все нормально у тебя со здоровьем. Ты пропустил этот ход и потерял энергию!");
                    playerEnergy -= 20;
                }
                if (playerEnergy < 20)
                {
                    Console.WriteLine("Не достаточно энергии. Ты пропустил этот ход!");
                }
                Console.ReadLine();
            }

            // Define bot action
            if (enemyEnergy < 12)
            {
                Console.WriteLine("Вирус восстанавливает энергию...");
                enemyEnergy += 15;
                Console.ReadLine();
            }
            else
            {
                if (enemyHealth <= 20 && enemyEnergy >= 20)
                {
                    Console.WriteLine("Вирус лечится!");
                    enemyHealth += 20;
                    enemyEnergy -= 20;
                    Console.ReadLine();
                }
                else
                {
                    int botMove = rnd.Next(1, 3);

                    if (botMove == 1 && enemyEnergy >= 12)
                    {
                        Console.WriteLine("Вирус атакует лёгкой атакой -10 урона!");
                        playerHealth -= 10;
                        enemyEnergy -= 12;
                        Console.ReadLine();
                    }
                    else if (botMove == 2 && enemyEnergy >= 20)
                    {
                        Console.WriteLine("Вирус атакует сильной атакой -20 урона!");
                        playerHealth -= 20;
                        enemyEnergy -= 20;
                        Console.ReadLine();
                    }
                    else
                    {
                        Console.WriteLine("Вирус восстанавливает энергию...");
                        enemyEnergy += 15;
                        Console.ReadLine();
                    }
                }
            }
        }
        Console.ReadLine();
    }
}