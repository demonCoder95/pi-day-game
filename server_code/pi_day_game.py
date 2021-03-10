"""This is going to be an instantiation of the GameTask
framework to implement one version of the q/a game

Author: Noor
Date: March 10, 2021

"""
# The class we'll use to design this game's tasks
from server_code.game_task import GameTask

# Keeping it in the form of a class to support future extension
class PiDayGame:
	game_intro = "=*"*40
	game_intro += "\n\n\nWelcome to  Pi-Day 2021 Game!\n\n\nYou will follow Pypy on his journey and help him solve puzzles.\nEach puzzle will earn you a set of points.\nYou will also have 2 hints, in total for the whole game.\nThe player with the highest score will be rewarded worthily.\n\nOh, and your progress will be automatically saved as you play along. No worries!\n\nLet's get started. Good luck!\n\n"
	game_intro += "NOTE: Some tasks may not have a hint available!\n"
	game_intro += "=*"*40 + "\n"

	game_outro = "=*"*40
	game_outro += "\nThanks for playing! Your answers (if any) have been saved. If you haven't finished the game, resume any time with 'start', if you have, check out the leaderboard with 'leaderboard' event command!\n"
	game_outro += "=*"*40

	task1 = GameTask(1, "In the starting of the adventure, Pypy comes across a statue of Julius Caesar. At the pedestal is written some gibberish. On looking closely, he realizes it's a code. He brings out his notebook and notes the following text written on the pedestal:\n'OHWWFWPKHF'.\nHelp him figure out what it means!\n",
	"It's a Caesar cipher encoded message.", "HAPPYPIDAY", 3)
	task2 = GameTask(2, "The previous puzzle was too easy and with the soaring confidence, Pypy now starts to head towards the market, thinking what better way to celebrate Pi-day than to eat a Pie!\nOn reaching his favorite French bakery Vigenere's, he sees a big note in the window. It reads:\n\nCelebrating Pi-Day with Pies!\nOur legendary owner wrote a message before he died, can you tell us what it means? You'll be rewarded for it! \nMVCMVOWAWCYYAZMOHYNK\n\nUnable to resist the temptation, our hero decides to solve this one as well. Help him!\n",
	"It's a Vigenere's with text reversed.", "IWASVERYHANDSOMEONCE", 5)
	task3 = GameTask(3, "Yummmm... Pypy is so glad to have that delicious apple Pie. He's heading into the market to see what kind of celebrations are in place.\nHe sees two children at a street corner arguing about something in a notebook.\n\nChild1: No, that's not right, it can't be.\nChild2: Of course it is, don't you see!\n\nPypy sneaks in and takes a look at the notebook and it is smeared with crosses and many attempts at solving the problem. He then looks at the very top of the page which reads:\n\nAn old man walks into a perfectly circular track of 20meters diameter at a speed of 3pi meters/min COUNTERCLOCKWISE.\nA cat walks onto the same track CLOCKWISE at pi meters/min.\nAfter 3 minutes of walking, what is the shortest distance between the man and the cat, divided by pi?\n\nPypy recalls from school geometry that a circlular track of radius r will be 2*pi*r meters long. He thinks he can do it.\n",
	"", "8", 7)
	task4 = GameTask(4, "The children were thrilled to watch a master at play with his calculations and their debate was settled for good. They thanked Pypy and gave him a boxful of candies all made up of round shapes and Pypy thanked them and moved on.\nInto the heart of the marketplace, he sees many stalls and the colorful surroundings surprise him. People cheering, eating, laughing, having a great time together, that's what Pi-day is all about!\nIn all of this, Pypy's eyes catch a glimpse of a banner that reads\n\n'DO YOU HAVE WHAT IT TAKES TO SOLVE THIS PUZZLE?'\n\nKnowing Pypy, he immediately walks upto the lady on the counter and asks what it is all about. She takes him into the tent which has a huge triangular chocolate on the table and she hands him the note which gives details of the puzzle. It reads:\n\n" + \
		"This is the Perfectly Symmetric Magic Chocolate of Righteous Triangles! It is carefully made out of chocolate units. If I tell you that one of the smaller sides is 10 chocolate units long. Can you tell me how many chocolate units are there in the whole chocolate?",
		"A symmetric right triangle will be the one with base=perpendicular.", "50", 6)

	task5 = GameTask(5, "The lady rewarded Pypy with a smaller version of the Magic Chocolate and Pypy carries it along with him, next to the box of candies he received from the children. He's tired now and is heading home. He walks past a construction site, which has tools lying around all of which measure quantities in Pi units, how strange! There are no workers or engineers around, perhaps they all went to get pies as well.\n\nSuddenly, he hears a soft meowww and starts looking here and there. A little above him, on the side, he sees a cute brown cat trapped on the top of a slanted peak made of planks. It appears that when the cat climbed on it, the planks behind her fell, all but one and she's now trapped. Between the cat and him is a huge pit full of metal parts and he knows for sure the cat would not survive the fall. It meows sadly knowing that there is no way she can get home and meet her baby kittens. Pypy knows that he can help the cat by using one of the planks lying around, but which one to choose?\n\nHe uses an engineer's protractor on the ground beside him to measure the angle that the cat makes with the ground from the point where he's standing. It turns out to be pi/3. He then uses a laser based instrument to measure the distance between him and the base of the slant on which the cat is trapped, it measures 10pi meters.\nPypy immediately knows which length of the plank to use to perfectly fit the distance between him and the cat. What is it(in pi meters)?\n",
	"", "20", 14)
	tasks = [task1, task2, task3, task4, task5]