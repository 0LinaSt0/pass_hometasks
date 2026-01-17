using SFML.Graphics;
using SFML.System;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Hw7CatchSquareOOP
{
    public class BlackSquare : Square
    {
        private static Color Color = new Color(50, 50, 50);
        private static float MiniSize = 30;
        private static float SizeStep = 10;
        public BlackSquare(Vector2f position, float movementSpeed, IntRect movementBounds) :
            base(position, movementSpeed, movementBounds)
        {
            shape.FillColor = Color;
        }

        protected override void OneClick()
        {
            Game.Scores++;

            shape.Size -= new Vector2f(SizeStep, SizeStep);

            if (shape.Size.X < MiniSize)
            {
                IsActive = false;
                return;
            }

            UpdateMovementTarget();
            shape.Position = movementTarget;
        }
    }
}
