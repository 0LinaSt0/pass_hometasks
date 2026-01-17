using SFML.Graphics;
using SFML.Window;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Hw7CatchSquareOOP
{
    class SquareList
    {
        private List<Square> squares;
        public bool SquareHasRemoved;
        public Square RemovedSquare;

        public SquareList()
        {
            squares = new List<Square>();
        }

        public void Reset()
        {
            SquareHasRemoved = false;
            RemovedSquare = null;
            squares.Clear();
        }

        public void Update(RenderWindow win)
        {
            SquareHasRemoved = false;
            RemovedSquare = null;

            if (Mouse.IsButtonPressed(Mouse.Button.Left) == true)
            {
                for (int i = 0; i < squares.Count; i++)
                {
                    squares[i].CheckMousePosition(Mouse.GetPosition(win));
                }
            }

            for (int i = 0; i < squares.Count; i++)
            {
                squares[i].Move();
                squares[i].Draw(win);

                if (squares[i].IsActive == false)
                {
                    RemovedSquare = squares[i];
                    squares.Remove(squares[i]);
                    SquareHasRemoved = true;
                }
            }
        }

        public void SpawnBlackSquare()
        {
            squares.Add(
                new BlackSquare(
                    new SFML.System.Vector2f(Mathf.Random.Next(0, 800), (Mathf.Random.Next(0, 600))), 
                    5, 
                    new IntRect(0, 0, 800, 600)
                )
            );
        }

        public void SpawnRedSquare()
        {
            squares.Add(
                new RedSquare(
                    new SFML.System.Vector2f(Mathf.Random.Next(0, 800), (Mathf.Random.Next(0, 600))),
                    5,
                    new IntRect(0, 0, 800, 600)
                )
            );
        }
    }
}
