# 2024 NewsPanda

This is a react app based repository which contains the WWF-Nepal-Dashboard and python-scripts that are run to run the entire pipeline for the Updated 2024 NewsPanda. 

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.


### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.


### Deployment

To deploy to the webpage.

You must first build the app with `npm run build`
And finally deploy with `firebase deploy`

# TO RUN WEEKLY PIPELINE FOR NEPAL

Go to python-scripts directory

Run `scrape-websites.py` script.

Run `combine-csvs-nepal.py` script.

Go to root directory.

Run `npm build`

Run `firebase deploy`

