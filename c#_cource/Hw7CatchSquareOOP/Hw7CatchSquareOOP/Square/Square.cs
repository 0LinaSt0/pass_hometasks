using System;
using SFML.Graphics;
using SFML.System;

namespace Hw7CatchSquareOOP
{
    public class Square
    {
        public bool IsActive = true;

        protected RectangleShape shape;
        protected float movementSpeed;
        protected Vector2f movementTarget;
        protected IntRect movementBounds;

        public Square(Vector2f position, float movementSpeed, IntRect movementBounds)
        {
            shape = new RectangleShape(new Vector2f(100, 100));
            shape.Position = position;

            this.movementSpeed = movementSpeed;
            this.movementBounds = movementBounds;

            UpdateMovementTarget();
        }

        public void Move()
        {
            shape.Position = Mathf.MoveTowards(shape.Position, movementTarget, movementSpeed);

            if (shape.Position == movementTarget)
            {
                OneReachedTarget();

                UpdateMovementTarget();
            }
        }

        public void Draw(RenderWindow win)
        {
            if (IsActive == false) return;

            win.Draw(shape);
        }

        public void CheckMousePosition(Vector2i mousePos)
        {
            if (IsActive == false) return;

            if (mousePos.X > shape.Position.X && mousePos.X < shape.Position.X + shape.Size.X &&
                mousePos.Y > shape.Position.Y && mousePos.Y < shape.Position.Y + shape.Size.Y)
                OneClick();
        }

        protected void UpdateMovementTarget()
        {
            movementTarget.X = Mathf.Random.Next(movementBounds.Left, movementBounds.Left + movementBounds.Width);
            movementTarget.Y = Mathf.Random.Next(movementBounds.Top, movementBounds.Top + movementBounds.Height);
        }

        protected virtual void OneClick() { }
        protected virtual void OneReachedTarget() { }
    }
}
