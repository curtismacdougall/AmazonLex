### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta
from botocore.vendored import requests

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

# function to provide portfolio reccomendation

def get_recommendation(risk_level):
    
        if (risk_level == 'none'):
            recommendation = "100% bonds (AGG), 0% equities (SPY)"    
            return recommendation
        elif (risk_level == 'very low'):
            recommendation = "80% bonds (AGG), 20% equities (SPY)"        
            return recommendation
        elif (risk_level == 'low'):
            recommendation = "60% bonds (AGG), 40% equities (SPY)"        
            return recommendation     
        elif (risk_level == 'medium'):
            recommendation = "40% bonds (AGG), 60% equities (SPY)"        
            return recommendation
        elif (risk_level == 'high'):
            recommendation = "20% bonds (AGG), 80% equities (SPY)"        
            return recommendation
        elif (risk_level == 'very high'):
            recommendation = "0% bonds (AGG), 100% equities (SPY)"        
            return recommendation


        
### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]

# Validates user inputs - age (between 0 and 65) and investment amount (5000 or more)
def validate_input_data(age, investment_amount, intent_request):

    if age is not None:
        age = parse_int(age)
    
        if  age <= 0:
            return build_validation_result(False,
                'age', 
                'This portfolio reccomendation tool is intended for individuals under age 65' 
                'Please enter an age between 0 and 65',)
        elif age >= 65:
            return build_validation_result(False,
                'age', 
                'This portfolio reccomendation tool is intended for individuals under age 65' 
                'Please enter an age between 0 and 65',)
        
    if investment_amount is not None:
        investment_amount = parse_int(investment_amount)
        
        if investment_amount < 5000:
            return build_validation_result(False,
                'investmentAmount',
                'The minimum investment amount is 5000'
                'Please enter a value of 5000 or greater to continue.',)
    
    return build_validation_result (True, None, None)
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        slots = get_slots(intent_request)
        # Perform basic validation on the supplied input slots.
        validation_result = validate_input_data(age, investment_amount, intent_request)
        # Use the elicitSlot dialog action to re-prompt
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None
        # for the first violation detected.
            return elicit_slot(
                    intent_request["sessionAttributes"],
                    intent_request["currentIntent"]["name"],
                    slots,
                    validation_result["violatedSlot"],
                    validation_result["message"],
                )
       
        

        ### YOUR DATA VALIDATION CODE STARTS HERE ###
        
        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation
    initial_recommendation = get_recommendation(risk_level)
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)

