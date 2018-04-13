# Luis App Manager for Python
This is a simple project used to create, delete, modify, train, publish [LUIS](https://www.luis.ai/) models. Forked from [this Microsoft repository](https://github.com/Microsoft/LUIS-Samples/blob/master/documentation-samples/authoring-api-samples/python/add-utterances-3-6.py).

## 1. Creating a App, adding utterances, training and publishing it
Creating your app with this code is as simple as it looks like. Follow the code:
```
luis = LUISApp('<LUIS Subscription key>')
luis.add_intent('BookFlight')
luis.add_utterances(utterance=['book a flight','i want to go to seattle','i want to go to brazil','book a flight to brazil','flight to brazil'],intent_name='BookFlight')
luis.train()
luis.publish()
```
