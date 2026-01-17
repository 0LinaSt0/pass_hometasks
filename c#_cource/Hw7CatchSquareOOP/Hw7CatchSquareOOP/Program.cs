using System;
using System.Collections.Generic;
using SFML.Graphics;
using SFML.Window;

namespace Hw7CatchSquareOOP
{
    public class Program
    {
        public static void Main(string[] args)
        {
            RenderWindow win = new RenderWindow(new VideoMode(800, 600), "Catchme");
            win.Closed += Win_Closed;
            win.SetFramerateLimit(60);

            Game game = new Game();


            while (win.IsOpen == true)
            {
                win.Clear(new Color(230, 230, 230));

                win.DispatchEvents();

                game.Update(win);

                win.Display();
            }
        }
        static void Win_Closed(object sender, EventArgs e)
        {
            ((RenderWindow)sender).Close();
        }
    }
}
