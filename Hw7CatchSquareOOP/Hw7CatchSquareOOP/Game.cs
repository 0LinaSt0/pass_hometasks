using SFML.Graphics;
using SFML.Window;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Hw7CatchSquareOOP
{
    public class Game
    {
        public static int Scores;
        public static bool IsLost;

        private Font mainFont;
        private Text scoreText;
        private Text loseText;

        private SquareList squares;

        private int maxScores;

        public Game()
        {
            mainFont = new Font("comic.ttf");
            squares = new SquareList();

            scoreText = new Text();
            scoreText.Font = mainFont;
            scoreText.FillColor = Color.Black;
            scoreText.CharacterSize = 16;
            scoreText.Position = new SFML.System.Vector2f(10, 10);

            loseText = new Text();
            loseText.Font = mainFont;
            loseText.FillColor = Color.Black;
            loseText.DisplayedString = "Game over! Press R for restart";
            loseText.Position = new SFML.System.Vector2f(20, 290);

            Reset();
        }

        private void Reset()
        {
            squares.Reset();
            Scores = 0;
            IsLost = false;

            squares.SpawnBlackSquare();
            squares.SpawnRedSquare();
        }

        public void Update(RenderWindow win)
        {
            if (IsLost == true) 
            {
                win.Draw(loseText);
                if (maxScores < Scores)
                {
                    maxScores = Scores;
                }
                if (Keyboard.IsKeyPressed(Keyboard.Key.R) == true)
                {
                    Reset();
                }
            }
            if (IsLost == false)
            {
                squares.Update(win);

                if (squares.SquareHasRemoved == true)
                {
                    if (squares.RemovedSquare != null)
                    {
                        squares.SpawnBlackSquare();
                    }
                }

                scoreText.DisplayedString = "Score: " + Scores.ToString() + "\nMax: " + maxScores.ToString();
                win.Draw(scoreText);
            }
        }
    }
}
