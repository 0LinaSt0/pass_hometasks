using System;
using SFML.Learning;
using SFML.Window;
using SFML.System;

class FindCouple : Game
{
    static string plusOneSound = LoadSound("plus_one.wav");

    static string[] iconsName;

    static int[,] cards;
    static int cardCount = 20;
    static int cardWidth = 100;
    static int cardHeight = 100;

    static int countPerLine = 5;
    static int space = 40;
    static int leftOffset = 70;
    static int topOffset = 20;

    static void LoadIcons()
    {
        iconsName = new string[6];

        for (int i = 0; i < iconsName.Length; i++)
        {
            iconsName[i] = LoadTexture("Icon_" + (i + 1).ToString() + ".png");
        }
    }

    static void Shuffle(int[] arr)
    {
        Random rnd = new Random();

        for (int i = arr.Length - 1; i >= 1; i--)
        {
            int j = rnd.Next(1, i + 1);

            int tmp = arr[j];
            arr[j] = arr[i];
            arr[i] = tmp;
        }
    }

    static void InitCard()
    {
        Random rnd = new Random();
        cards = new int[cardCount, 6];

        int[] iconId = new int[cards.GetLength(0)];
        int id = 0;

        for (int i = 0; i < iconId.Length; i++)
        {
            if (i % 2 == 0) id = rnd.Next(0, 6);

            iconId[i] = id;
        }

        Shuffle(iconId);
        Shuffle(iconId);
        Shuffle(iconId);

        for (int i = 0; i < cards.GetLength(0); i++)
        {
            cards[i, 0] = 1; //state
            cards[i, 1] = (i % countPerLine) * (cardWidth + space) + leftOffset; // posX
            cards[i, 2] = (i / countPerLine) * (cardHeight + space) + topOffset; // posY
            cards[i, 3] = cardWidth; // width
            cards[i, 4] = cardHeight; // height
            cards[i, 5] = iconId[i]; // id
        }
    }

    static void DrawCards()
    {
        for (int i = 0; i < cards.GetLength(0); i++)
        {
            if (cards[i, 0] == 1) // open
            {
                DrawSprite(iconsName[cards[i, 5]], cards[i, 1], cards[i, 2]);
                //if (cards[i, 5] == 1) { SetFillColor(0, 100, 0); FillRectangle(cards[i, 1], cards[i, 2], cards[i, 3], cards[i, 4]); }
                //if (cards[i, 5] == 2) { SetFillColor(0, 100, 100); FillRectangle(cards[i, 1], cards[i, 2], cards[i, 3], cards[i, 4]); }
                //if (cards[i, 5] == 3) { SetFillColor(0, 0, 100); FillRectangle(cards[i, 1], cards[i, 2], cards[i, 3], cards[i, 4]); }
                //if (cards[i, 5] == 4) { SetFillColor(100, 100, 0); FillRectangle(cards[i, 1], cards[i, 2], cards[i, 3], cards[i, 4]); }
                //if (cards[i, 5] == 5) { SetFillColor(100, 100, 100); FillRectangle(cards[i, 1], cards[i, 2], cards[i, 3], cards[i, 4]); }
                //if (cards[i, 5] == 6) { SetFillColor(100, 0, 100); FillRectangle(cards[i, 1], cards[i, 2], cards[i, 3], cards[i, 4]); }
            }
            else if (cards[i, 0] == 0) // close
            {
                SetFillColor(30, 30, 30);
                FillRectangle(cards[i, 1], cards[i, 2], cards[i, 3], cards[i, 4]);
            }
        }
    }

    static int GetIndexCardsByMousePosition()
    {
        for (int i = 0; i < cards.GetLength(0); i++)
        {
            if (MouseX >= cards[i, 1]
            && MouseX <= cards[i, 1] + cards[i, 3]
            && MouseY >= cards[i, 2]
            && MouseY <= cards[i, 2] + cards[i, 4])
            {
                return i;
            }
        }
        return -1;
    }

    static void SetStateToAllCards(int state = 0)
    {
        for (int i = 0; i < cards.GetLength(0); i++) cards[i, 0] = state;
    }
    static void Main(string[] args)
    {
        InitWindow(800, 600, "Find Couple");
        SetFont("comic.ttf");

        LoadIcons();
        InitCard();
        SetStateToAllCards(1);

        // Стартовый показ карт 5 сек
        DrawCards();
        DisplayWindow();
        Delay(5000);
        SetStateToAllCards(0);

        int openCardAmount = 0;
        int firstOpenCardIndex = -1;
        int secondOpenCardIndex = -1;
        int remindingCards = cardCount;

        
        while (true)
        {
            // 1. Расчет
            DispatchEvents();

            if (remindingCards == 0) break;

            if (openCardAmount == 2)
            {
                if (cards[firstOpenCardIndex, 5] == cards[secondOpenCardIndex, 5])
                {
                    cards[firstOpenCardIndex, 0] = -1;
                    cards[secondOpenCardIndex, 0] = -1;

                    remindingCards -= 2;
                }
                else
                {
                    cards[firstOpenCardIndex, 0] = 0;
                    cards[secondOpenCardIndex, 0] = 0;
                }

                firstOpenCardIndex = -1;
                secondOpenCardIndex = -1;

                openCardAmount = 0;

                Delay(500);
            }

            if (GetMouseButtonDown(0) == true)
            {
                PlaySound(plusOneSound);
                int index = GetIndexCardsByMousePosition();

                if (index != -1 && index != firstOpenCardIndex)
                {
                    cards[index, 0] = 1;
                    openCardAmount++;

                    if (openCardAmount == 1) firstOpenCardIndex = index;
                    if (openCardAmount == 2) secondOpenCardIndex = index;
                }
            }

            //2.Отчистка
            ClearWindow();

            // 3. Отрисовка
            DrawCards();

            DisplayWindow();

            // 4. Ожидание
            Delay(1);
        }

        // Конец игры
        ClearWindow();

        SetFillColor(255, 0, 0);
        DrawText(300, 300, "Game over, winner!", 24);

        DisplayWindow();
        Delay(2500);
    }
}
