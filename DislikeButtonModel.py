songs = []
disliked = []
song_title = input("Enter the EXACT song title you dislike: ").lower()
for i in songs:
    if i == song_title:
        disliked.append(i)
