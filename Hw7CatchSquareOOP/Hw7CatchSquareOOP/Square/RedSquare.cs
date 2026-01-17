using SFML.Graphics;
using SFML.System;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Hw7CatchSquareOOP
{
    public class RedSquare : Square
    {
        private static Color Color = new Color(230, 50, 50);
        private static float MaxMovementSpeed = 3;
        private static float MovementStep = 0.05f;
        private static float MaxSize = 150;
        private static float SizeStep = 10;
        public RedSquare(Vector2f position, float movementSpeed, IntRect movementBounds) :
            base(position, movementSpeed, movementBounds)
        {
            shape.FillColor = Color;
        }

        protected override void OneClick()
        {
            Game.IsLost = true;
        }

        protected override void OneReachedTarget()
        {
            if (movementSpeed < MaxMovementSpeed)
            {
                movementSpeed += MovementStep;
            }

            if (shape.Size.X < MaxSize)
                shape.Size += new Vector2f(SizeStep, SizeStep);
        }
    }
}
