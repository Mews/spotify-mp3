To use the spotify-mp3 app, you will need to provide a client id to connect to the spotify api
---

To get yours, first naviagate to the [spotify developer portal](https://developer.spotify.com/) and log in at the top right corner.

Then, go the [dashboard](https://developer.spotify.com/dashboard) and create an app.

![Create app](https://i.ibb.co/wN1yW31/image.png)

Give it any name and description you want, and leave the "website" section empty.

Then, in the "Redirect URI" section, enter `http://localhost:8888/callback`.

In the "Which API/SDKs are you planning to use?" section, select "Web API".

Your app should look something like this

![App configuration](https://i.ibb.co/kBSSr2C/image.png)\
Press the save button.

Once your app is created, open the app settings.

![Settings](https://i.ibb.co/hdLP0RV/image.png)

Finally, under "basic information", you'll see your client id and client secret.

![Client id](https://i.ibb.co/XJ7WmQR/image.png)

