using SFML.Graphics;
using SFML.System;

internal class Ball
{
    public Sprite sprite;

    public bool IsLost { get; private set; } = false;

    private float speed;
    private Vector2f direction;

    public Ball(Texture texture)
    {
        sprite = new Sprite(texture);
    }

    public void Start(float speed, Vector2f direction)
    {
        if (this.speed != 0) return;
        
        this.speed = speed;
        this.direction = direction;   
    }

    
    public void Move(Vector2i boundsPos, Vector2i boundsSize)
    {
        if (this.IsLost) return;  // Не двигать после проигрыша

        this.sprite.Position += this.direction * this.speed;

        if (this.sprite.Position.X > boundsSize.X - this.sprite.Texture.Size.X ||
            this.sprite.Position.X < boundsPos.X)
        {
            this.direction.X *= -1;
        }
        if (this.sprite.Position.Y < boundsPos.Y)
        {
            this.direction.Y *= -1;
        }
        if (this.sprite.Position.Y > boundsSize.Y)
        {
            this.IsLost = true;
        }
    }

    public bool CheckCollision(Sprite sprite, string tag)
    {
        if (this.sprite.GetGlobalBounds().Intersects(
            sprite.GetGlobalBounds()
        ) == true)
        {
            if (tag == "stick")
            {
                this.direction.Y = -1;

                float f = (
                    ((this.sprite.Position.X + this.sprite.Texture.Size.X * 0.5f)
                    - (sprite.Position.X + sprite.Texture.Size.X * 0.5f)) // distance between ball and center of stick
                    / sprite.Texture.Size.X * 0.5f // deflection angle
                );

                this.direction.X = f * 2;

            }
            if (tag == "block")
            {
                this.direction.Y *= -1;

            }

            return true;
        }

        return false;
    }

    public void Reset(Vector2f startPos)
    {
        this.sprite.Position = startPos;
        this.direction = new Vector2f(0, 0);
        this.speed = 0;
        this.IsLost = false;
    }
}
