from db import session
import classes as cls

from flask.ext.restful import reqparse
from flask.ext.restful import abort
from flask.ext.restful import fields
from flask.ext.restful import marshal_with
import json
from auth import login_required
import requests
from flask import g,request

from value_distributer import ValueDistributer 
from datetime import datetime

#from flask.ext.restful import Resource
#Add Authentication required to all resources:
from flask.ext.restful import Resource as FlaskResource
from milestone_value_distributer import MileStoneValueDistributer
class Resource(FlaskResource):
   method_decorators = [login_required]   # applies to all inherited resources

userParser = reqparse.RequestParser()
userOrganizationParser = reqparse.RequestParser()
contributionParser = reqparse.RequestParser()
milestoneParser = reqparse.RequestParser()
bidParser = reqparse.RequestParser()
mileStonebidParser = reqparse.RequestParser()
closeContributionParser = reqparse.RequestParser()

contributionParser.add_argument('contributers', type=cls.Contributer, action='append')
contributionParser.add_argument('owner', type=int,required=True)
contributionParser.add_argument('users_organizations_id', type=int,required=True)
contributionParser.add_argument('min_reputation_to_close', type=str)
contributionParser.add_argument('file', type=str,required=True)
contributionParser.add_argument('title', type=str)

milestoneParser.add_argument('owner', type=int,required=True)
milestoneParser.add_argument('users_organizations_id', type=int,required=True)
milestoneParser.add_argument('description', type=str,required=True)
milestoneParser.add_argument('title', type=str)
milestoneParser.add_argument('evaluatingTeam', type=int,required=True)

userParser.add_argument('userId', type=str)
userParser.add_argument('name', type=str,required=True)
userParser.add_argument('slack_id', type=str)


bidParser.add_argument('stake', type=str,required=True)
bidParser.add_argument('tokens', type=str,required=True)
bidParser.add_argument('reputation', type=str,required=True)    
bidParser.add_argument('contribution_id', type=str,required=True)
bidParser.add_argument('owner', type=int,required=True)

mileStonebidParser.add_argument('stake', type=str,required=True)
mileStonebidParser.add_argument('tokens', type=str,required=True)
mileStonebidParser.add_argument('reputation', type=str,required=True)    
mileStonebidParser.add_argument('milestone_id', type=str,required=True)
mileStonebidParser.add_argument('owner', type=int,required=True)

closeContributionParser.add_argument('owner', type=int,required=True)
closeContributionParser.add_argument('id', type=int,required=True)

user_fields = {
    'id': fields.Integer,
    'name': fields.String,    
}

user_org_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'tokens': fields.String,  
    'reputation': fields.String, 
     'url' : fields.String,
     'real_name':fields.String,
}

org_fields = {
    'id': fields.Integer,
    'name': fields.String, 
    'token_name': fields.String,
    'channelName': fields.String,      
}

userOrganization_fields = {
    'id': fields.Integer,
    'user_id': fields.String,
    'organization_id': fields.String,
    'org_tokens': fields.String,
    'org_reputation': fields.String,
    'channelId':fields.String
}

bid_fields = {
    'id': fields.Integer,
    'contribution_id': fields.Integer
}

bid_nested_fields = {}
bid_nested_fields['stake'] = fields.String
bid_nested_fields['tokens'] = fields.String
bid_nested_fields['reputation'] = fields.String
bid_nested_fields['owner'] = fields.Integer
bid_nested_fields['bidderName'] = fields.String

bid_status_nested_fields = {}
bid_status_nested_fields['time_created'] = fields.String
bid_status_nested_fields['tokens'] = fields.String
bid_status_nested_fields['reputation'] = fields.String
bid_status_nested_fields['contribution_value_after_bid'] = fields.Float
bid_status_nested_fields['stake'] = fields.Float
bid_status_nested_fields['owner'] = fields.Integer

contributer_nested_fields = {}
contributer_nested_fields['contributer_id'] = fields.String
contributer_nested_fields['contributer_percentage'] = fields.String
contributer_nested_fields['name'] = fields.String
contributer_nested_fields['real_name'] = fields.String
contributer_nested_fields['url'] = fields.String
contributer_nested_fields['project_reputation'] = fields.String

contribution_fields = {}
contribution_fields['id'] = fields.Integer
contribution_fields['time_created'] = fields.DateTime
contribution_fields['users_organizations_id'] = fields.Integer
contribution_fields['status'] = fields.String
contribution_fields['owner'] = fields.String
contribution_fields['file'] = fields.String
contribution_fields['title'] = fields.String
contribution_fields['tokenName'] = fields.String
contribution_fields['code'] = fields.String
contribution_fields['channelId'] = fields.String
contribution_fields['currentValuation'] = fields.Integer
contribution_fields['bids'] = fields.Nested(bid_nested_fields)
contribution_fields['contributionContributers'] = fields.Nested(contributer_nested_fields)

contribution_status_fields ={}
contribution_status_fields['currentValuation'] = fields.Integer
contribution_status_fields['reputationDelta'] = fields.Integer
contribution_status_fields['myValuation'] = fields.Integer
contribution_status_fields['myWeight'] = fields.Float
contribution_status_fields['groupWeight'] = fields.Float
contribution_status_fields['project_reputation'] = fields.Float
contribution_status_fields['totalSystemReputation'] = fields.Float
contribution_status_fields['file'] = fields.String
contribution_status_fields['title'] = fields.String
contribution_status_fields['bids'] = fields.Nested(bid_status_nested_fields)
contribution_status_fields['contributionContributers'] = fields.Nested(contributer_nested_fields)

contribution_status_nested_fields ={}
contribution_status_nested_fields['currentValuation'] = fields.Integer
contribution_status_nested_fields['reputationDelta'] = fields.Integer
contribution_status_nested_fields['id'] = fields.Integer
contribution_status_nested_fields['myWeight'] = fields.Float
contribution_status_nested_fields['title'] = fields.String
contribution_status_nested_fields['cTime'] = fields.String
contribution_status_nested_fields['tokenName'] = fields.String
contribution_status_nested_fields['owner'] = fields.String


member_status_fields ={}
member_status_fields['project_tokens'] = fields.String
member_status_fields['tokenName'] = fields.String
member_status_fields['code'] = fields.String
member_status_fields['project_reputation'] = fields.String
member_status_fields['contributionLength'] = fields.String
member_status_fields['url'] = fields.String
member_status_fields['fullName'] = fields.String
member_status_fields['name'] = fields.String
member_status_fields['reputationPercentage'] = fields.String
member_status_fields['contributions'] = fields.Nested(contribution_status_nested_fields)



milestoneContributer_nested_fields = {}
milestoneContributer_nested_fields['contributer_id'] = fields.String
milestoneContributer_nested_fields['contributer_percentage'] = fields.String
milestoneContributer_nested_fields['name'] = fields.String
milestoneContributer_nested_fields['real_name'] = fields.String
milestoneContributer_nested_fields['url'] = fields.String

contribution_contributer_nested_fields = {}
contribution_contributer_nested_fields['memberId'] = fields.String
contribution_contributer_nested_fields['url'] = fields.String

milestoneContribution_nested_fields = {}
milestoneContribution_nested_fields['title'] = fields.String
milestoneContribution_nested_fields['description'] = fields.String
milestoneContribution_nested_fields['date'] = fields.String
milestoneContribution_nested_fields['valuation'] = fields.String
milestoneContribution_nested_fields['contribution_id'] = fields.Integer
milestoneContribution_nested_fields['remainingContributers'] = fields.Integer
milestoneContribution_nested_fields['contributers'] = fields.Nested(contribution_contributer_nested_fields)



milestone_fields = {}
milestone_fields['id'] = fields.Integer
milestone_fields['current_org_id'] = fields.Integer
milestone_fields['start_date'] = fields.DateTime
milestone_fields['end_date'] = fields.DateTime
milestone_fields['users_organizations_id'] = fields.Integer
milestone_fields['owner'] = fields.String
milestone_fields['description'] = fields.String
milestone_fields['tokens'] = fields.Float
milestone_fields['totalValue'] = fields.Float
milestone_fields['contributions'] = fields.Integer
milestone_fields['contributers'] = fields.Integer
milestone_fields['title'] = fields.String
milestone_fields['tokenName'] = fields.String
milestone_fields['channelName'] = fields.String
milestone_fields['code'] = fields.String
milestone_fields['destination_org_id'] = fields.Integer
milestone_fields['milestoneContributers'] = fields.Nested(milestoneContributer_nested_fields)
milestone_fields['milestoneContributions'] = fields.Nested(milestoneContribution_nested_fields)



def getUser(id):
    user = session.query(cls.User).filter(cls.User.id == id).first()    
    return user
   
class UserResource(Resource):
    @marshal_with(user_org_fields)
    def get(self, id,orgId):
        char = getUser(id)
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).filter(cls.UserOrganization.user_id == id).first()
        print 'got Get for User fbid:'+id
        if not char:
            abort(404, message="User {} doesn't exist".format(id))       
        return {"id": char.id,"name":char.name,"tokens": userOrgObj.org_tokens,"reputation": userOrgObj.org_reputation} 
    
    def delete(self, id):
        char = getUser(id)
        if not char:
            abort(404, message="User {} doesn't exist".format(id))
        session.delete(char)
        session.commit()
        return {}, 204

    @marshal_with(user_fields)
    def put(self, id):
        parsed_args = userParser.parse_args()
        char = getUser(id)
        session.add(char)
        session.commit()
        return char, 201

    @marshal_with(user_fields)
    def post(self):
        parsed_args = userParser.parse_args()

        jsonStr = {
                    "name":parsed_args['name']
                    }
        user = cls.User(jsonStr,session)

        session.add(user)
        session.commit()
        return user, 201
    
class AllOrganizationResource(Resource):
    @marshal_with(org_fields)
    def get(self):
        organizations = session.query(cls.Organization).all()
        return organizations
    
class AllOrganizationForCurrentTeamResource(Resource):
    @marshal_with(org_fields)
    def get(self,slackTeamId):
        organizations = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).all()
        return organizations
    
class AllUserResource(Resource):
    @marshal_with(user_org_fields)
    def get(self,organizationId):
        users =[]    
        userOrganizationObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == organizationId).all()
        for userOrganization in userOrganizationObjects :
            print 'url is'+str(userOrganization.user.url)
            users.append({'url':userOrganization.user.url,'real_name':userOrganization.user.real_name,'id':userOrganization.user.id,'name':userOrganization.user.name,"tokens": userOrganization.org_tokens,"reputation": userOrganization.org_reputation})           
        return users
        
class BidResource(Resource):
    @marshal_with(bid_fields)
    def get(self, id):
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        print 'got Get for Bid fbid:'+id
        if not char:
            abort(404, message="Bid {} doesn't exist".format(id))
        return char

    def delete(self, id):
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        if not char:
            abort(404, message="Bid {} doesn't exist".format(id))
        session.delete(char)
        session.commit()
        return {}, 204

    @marshal_with(bid_fields)
    def put(self, id):
        parsed_args = bidParser.parse_args()
        char = session.query(cls.Bid).filter(cls.Bid.id == id).first()
        session.add(char)
        session.commit()
        return char, 201

    @marshal_with(bid_fields)
    def post(self):
        parsed_args = bidParser.parse_args()
        contributionid = parsed_args['contribution_id']        
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionid).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionid))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is not Open".format(contributionid))
        userObj = getUser(parsed_args['owner'])        
        if not userObj:
            abort(404, message="User {} who is creating bid  doesn't exist".format(parsed_args['owner']))     
        jsonStr = {"tokens":parsed_args['tokens'],
                   "reputation":parsed_args['reputation'],
                   "owner":parsed_args['owner'],
                   "contribution_id":parsed_args['contribution_id'],
                   "stake":parsed_args['stake'], 
                   "time_created":datetime.now()
                    }

        bid = cls.Bid(jsonStr,session) 
        vd = ValueDistributer()
        vd.process_bid(bid,session)
        if(vd.error_occured):
            print vd.error_code
            # ToDo :  pass correct error message to user
            abort(404, message="Failed to process bid".format(contributionid))

        return bid, 201
    
class MileStoneBidResource(Resource):
    @marshal_with(bid_fields)
    def get(self, id):
        char = session.query(cls.MileStoneBid).filter(cls.MileStoneBid.id == id).first()
        print 'got Get for MileStoneBid fbid:'+id
        if not char:
            abort(404, message="MileStoneBid {} doesn't exist".format(id))
        return char

    def delete(self, id):
        char = session.query(cls.MileStoneBid).filter(cls.MileStoneBid.id == id).first()
        if not char:
            abort(404, message="MileStoneBid {} doesn't exist".format(id))
        session.delete(char)
        session.commit()
        return {}, 204
    

    @marshal_with(bid_fields)
    def post(self):
        parsed_args = mileStonebidParser.parse_args()
        mileStoneId = parsed_args['milestone_id']        
        mileStoneObject = session.query(cls.MileStone).filter(cls.MileStone.id == mileStoneId).first()
        if not mileStoneObject:
            abort(404, message="MileStone {} doesn't exist".format(mileStoneId))        
        userObj = getUser(parsed_args['owner'])        
        if not userObj:
            abort(404, message="User {} who is creating bid  doesn't exist".format(parsed_args['owner']))     
        jsonStr = {"tokens":parsed_args['tokens'],
                   "reputation":parsed_args['reputation'],
                   "owner":parsed_args['owner'],
                   "milestone_id":parsed_args['milestone_id'],
                   "stake":parsed_args['stake'], 
                   "time_created":datetime.now()
                    }

        bid = cls.MileStoneBid(jsonStr,session) 
        vd = MileStoneValueDistributer()
        vd.process_bid(bid,session)
        if(vd.error_occured):
            print vd.error_code
            # ToDo :  pass correct error message to user
            abort(404, message="Failed to process bid".format(mileStoneId))

        return bid, 201
    
class BidContributionResource(Resource):
    def get(self, contributionId,userId):
        char = session.query(cls.Bid).filter(cls.Bid.contribution_id == contributionId).filter(cls.Bid.owner == userId).first()   
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first() 
        if contributionObject.status == 'Closed':
            return {"contributionClose":"true"}  
        if not char:
            return {"contributionClose":"false","bidExists":"false","organizationId":contributionObject.userOrganization.organization_id}
        else:
            return {"contributionClose":"false","bidExists":"true"} 
        
        
class MileStoneBidContributionResource(Resource):
    def get(self, mileStoneId,userId):
        char = session.query(cls.MileStoneBid).filter(cls.MileStoneBid.milestone_id == mileStoneId).filter(cls.MileStoneBid.owner == userId).first()   
        mileStoneObject = session.query(cls.MileStone).filter(cls.MileStone.id == mileStoneId).first()        
        if not char:
            return {"bidExists":"false","organizationId":mileStoneObject.userOrganization.organization_id}
        else:
            return {"bidExists":"true"}       

class ContributionResource(Resource):
    @marshal_with(contribution_fields)
    def get(self, id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        for contributer in contributionObject.contributionContributers:
            contributer.name= getUser(contributer.contributer_id).name
        last_bid = None 
        currentValuation = 0      
        for bid in contributionObject.bids:
            bid.bidderName = getUser(bid.owner).name
            last_bid = bid
            
        if (last_bid):
            currentValuation = last_bid.contribution_value_after_bid
        contributionObject.tokenName = contributionObject.userOrganization.organization.token_name
        contributionObject.currentValuation = currentValuation
        contributionObject.code = contributionObject.userOrganization.organization.code

        return contributionObject

    def delete(self, id):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        for contributer in contributionObject.contributionContributers:
            session.delete(contributer)
        for bid in contributionObject.bids:
            session.delete(bid)
        session.delete(contributionObject)
        session.commit()
        return {}, 204
    
    @marshal_with(contribution_fields)   
    def post(self):        
        parsed_args = contributionParser.parse_args()  
        contribution = cls.Contribution()
        contribution.owner = parsed_args['owner']
        contribution.min_reputation_to_close = parsed_args['min_reputation_to_close']
        contribution.file = parsed_args['file']
        contribution.owner = parsed_args['owner']
        contribution.title = parsed_args['title']
        contribution.users_organizations_id = parsed_args['users_organizations_id']
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.id == parsed_args['users_organizations_id']).first()
        userObj = getUser(contribution.owner) 
               
        if not userObj:
            abort(404, message="User who is creating contribution {} doesn't exist".format(contribution.owner))    
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.users_organizations_id == parsed_args['users_organizations_id']).first()
        firstContribution = False
        if (not contributionObject ):
            firstContribution = True
        for contributer in parsed_args['contributers']:             
            contributionContributer = cls.ContributionContributer()
            contributionContributer.contributer_id = contributer.obj1['contributer_id']
            if contributionContributer.contributer_id == '':
                continue
            userObj = getUser(contributionContributer.contributer_id)        
            if not userObj:
                abort(404, message="Contributer {} doesn't exist".format(contributionContributer.contributer_id))
            contributionContributer.contribution_id=contribution.id
            contributionContributer.name = userObj.name          
            contributionContributer.contributer_percentage=contributer.obj1['contributer_percentage']
            #if (firstContribution == True):
                 #userOrgObject = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).filter(cls.UserOrganization.user_id == userObj.id).first()
                 #if userOrgObject:
                    #userOrgObject.org_reputation = contributer.obj1['contributer_percentage']
                    #session.add(userOrgObject)                                               
            contribution.contributionContributers.append(contributionContributer)  
        if(len(contribution.contributionContributers) == 0):
            contributionContributer = cls.ContributionContributer()
            contributionContributer.contributer_id = contribution.owner
            contributionContributer.contributer_percentage = '100'
            contributionContributer.name = userObj.name
            contribution.contributionContributers.append(contributionContributer)  
            #if (firstContribution == True):
                #userOrgObjectForOwner.org_reputation = 100
                #session.add(userOrgObjectForOwner) 
                                
        #if((parsed_args['intialBid'].obj1['tokens'] != '') & (parsed_args['intialBid'].obj1['reputation'] != '')):      
                #jsonStr = {"tokens":parsed_args['intialBid'].obj1['tokens'],
                   #"reputation":parsed_args['intialBid'].obj1['reputation'],
                   #"owner":contribution.owner,
                   #"contribution_id":contribution.id
                    #}
                #intialBidObj = cls.Bid(jsonStr,session)        
                #contribution.bids.append(intialBidObj)
        
        
        
        session.add(contribution)
        session.commit()        
        contribution.channelId = userOrgObjectForOwner.organization.channelId
        return contribution, 201


class CloseContributionResource(Resource):
    @marshal_with(contribution_fields)   
    def post(self):      
        parsed_args = closeContributionParser.parse_args()   
        ownerId = parsed_args['owner'] 
        contributionId = parsed_args['id'] 
        userObj = getUser(ownerId)  
        if not userObj:
            abort(404, message="User who is closing contribution {} doesn't exist".format(ownerId)) 
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == contributionId).first()
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(contributionId))
        if contributionObject.status != 'Open':
            abort(404, message="Contribution {} is already closed".format(contributionId))        
        if userObj.id != contributionObject.owner:
            abort(404, message="Only contribution owner can close this contribution".format(ownerId)) 
        
        # process contribution:
        if( not self.process_contribution(contributionObject) ):
            abort(404, message="Failed to process contribution".format(contributionId))

        # success: close contribution and commit DB session:
        contributionObject.status='Closed'
        session.add(contributionObject)
        session.commit()        
       
        return contributionObject, 201


    def process_contribution(self,contribution):
        print 'process_contribution contribution bids:\n'+str(contribution.bids)
        
        return True


class AllContributionResource(Resource):
    @marshal_with(contribution_fields)
    def get(self,organizationId):
        if organizationId == 'notintialized':
            organizationId = 1
        contributionObject = session.query(cls.Contribution).filter(cls.UserOrganization.organization_id == organizationId).filter(cls.Contribution.users_organizations_id ==cls.UserOrganization.id).all()
        return contributionObject
    
class ContributionStatusResource(Resource):
    @marshal_with(contribution_status_fields)
    def get(self,id,userId):
        contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == id).first()
        print 'got Get for Contribution fbid:'+id
        if not contributionObject:
            abort(404, message="Contribution {} doesn't exist".format(id))
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == userId).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).all()
        totalSystemReputation = 0
        for userOrgObjVar in userOrgObjs :
            totalSystemReputation = totalSystemReputation + userOrgObjVar.org_reputation
        contributionObject.totalSystemReputation = totalSystemReputation
        currentValuation = 0
        myValuation = 0
        myWeight = 0
        groupWeight = 0
        reputationDelta = 0
        last_bid = None
        for contributer in contributionObject.contributionContributers:
            contributer.name= getUser(contributer.contributer_id).name
            contributer.url= getUser(contributer.contributer_id).url
            contributer.real_name= getUser(contributer.contributer_id).real_name
            contributerUserOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == contributer.contributer_id).filter(cls.UserOrganization.organization_id == contributionObject.userOrganization.organization_id).first()
            contributer.project_reputation = contributerUserOrgObj.org_reputation
        for bid in contributionObject.bids:
            last_bid = bid
            groupWeight = groupWeight + bid.weight
            if(str(bid.owner) == str(userId)):
                myWeight = bid.weight 
                reputationDelta = userOrgObj.org_reputation - bid.reputation
                myValuation = bid.tokens
        if (last_bid):
            currentValuation = last_bid.contribution_value_after_bid
        contributionObject.currentValuation = currentValuation
        contributionObject.reputationDelta = reputationDelta
        contributionObject.myValuation = myValuation
        contributionObject.myWeight = myWeight
        contributionObject.groupWeight = groupWeight
        contributionObject.project_reputation = userOrgObj.org_reputation
        return contributionObject
    
class MemberStatusAllOrgsResource(Resource):
    @marshal_with(member_status_fields)
    def get(self,slackTeamId,userId):        
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == cls.User.id).filter(cls.User.slackId == userId).filter(cls.UserOrganization.organization_id == cls.Organization.id).filter(cls.Organization.slack_teamid == slackTeamId).all()
        userOrgObj = userOrgObjs[0]
        allContributions = session.query(cls.Contribution).all()
        currentValuation = 0
        myWeight = 0
        reputationDelta = 0
        userOrgObj.name = userOrgObj.user.name
        userOrgObj.fullName = userOrgObj.user.real_name
        userOrgObj.url = userOrgObj.user.url72
        countOfContribution = 0  
        userOrgObj.reputationPercentage = 'N/A'
        
        last_bid = None
        for contribution in allContributions:
            contributedCounted = False
            if(str(contribution.owner) == str(userOrgObj.user.id)):
                countOfContribution = countOfContribution + 1
                contributedCounted = True
            if contributedCounted == False:
                for contributionContributer in contribution.contributionContributers :
                    if(str(contributionContributer.contributer_id) == str(userOrgObj.user.id)):
                        countOfContribution = countOfContribution + 1
                        contributedCounted = True
            if contributedCounted == True:
                last_bid = None
                currentValuation = 0
                myWeight = 0
                reputationDelta = 0
                for bid in contribution.bids:
                    last_bid = bid
                    if(str(bid.owner) == str(userOrgObj.user.id)):
                        myWeight = bid.weight 
                        reputationDelta = userOrgObj.org_reputation - bid.reputation
                if (last_bid):
                    currentValuation = last_bid.contribution_value_after_bid
                contribution.currentValuation = currentValuation
                contribution.reputationDelta = reputationDelta
                contribution.myWeight = myWeight
                contribution.tokenName= contribution.userOrganization.organization.token_name
                contribution.cTime = contribution.time_created.date()
                if userOrgObj.id != contribution.userOrganization.id :
                    userOrgObj.contributions.append(contribution)
        for contribution in userOrgObj.contributions:
            print 'contribution.myWeight'+str(contribution.myWeight)
        userOrgObj.contributionLength = countOfContribution
        userOrgObj.org_tokens = 'N/A'
        userOrgObj.org_reputation = 'N/A'
        return userOrgObj    


class MemberStatusResource(Resource):
    @marshal_with(member_status_fields)
    def get(self,orgId,userId):        
        userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == cls.User.id).filter(cls.User.slackId == userId).filter(cls.UserOrganization.organization_id == orgId).first()
        userOrgObjs = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).all()
        allContributions = session.query(cls.Contribution).filter(cls.UserOrganization.id == cls.Contribution.users_organizations_id).filter(cls.UserOrganization.organization_id == orgId).all()
        totalReputation = 0;
        for userOrgObjVar in userOrgObjs:
            totalReputation = totalReputation + userOrgObjVar.org_reputation
        currentValuation = 0
        myWeight = 0
        reputationDelta = 0
        userOrgObj.name = userOrgObj.user.name
        userOrgObj.fullName = userOrgObj.user.real_name
        userOrgObj.url = userOrgObj.user.url72
        
        userOrgObj.reputationPercentage = (userOrgObj.org_reputation / totalReputation)*100
        userOrgObj.project_tokens = userOrgObj.org_tokens
        userOrgObj.project_reputation = userOrgObj.org_reputation
        userOrgObj.tokenName = userOrgObj.organization.token_name
        userOrgObj.code = userOrgObj.organization.code
        last_bid = None
        countOfContribution = 0       
        for contribution in allContributions:
            contributedCounted = False
            if(str(contribution.owner) == str(userOrgObj.user.id)):
                countOfContribution = countOfContribution + 1
                contributedCounted = True
            if contributedCounted == False:
                for contributionContributer in contribution.contributionContributers :
                    if(str(contributionContributer.contributer_id) == str(userOrgObj.user.id)):
                        countOfContribution = countOfContribution + 1
                        contributedCounted = True
            if contributedCounted == True:
                last_bid = None
                currentValuation = 0
                myWeight = 0
                reputationDelta = 0
                for bid in contribution.bids:
                    last_bid = bid
                    if(str(bid.owner) == str(userOrgObj.user.id)):
                        myWeight = bid.weight 
                        reputationDelta = userOrgObj.org_reputation - bid.reputation
                if (last_bid):
                    currentValuation = last_bid.contribution_value_after_bid
                contribution.currentValuation = currentValuation
                contribution.reputationDelta = reputationDelta
                contribution.myWeight = myWeight
                contribution.cTime = contribution.time_created.date()
                contribution.tokenName= contribution.userOrganization.organization.token_name
                if(str(contribution.owner) != str(userOrgObj.user.id)):
                    userOrgObj.contributions.append(contribution)
        userOrgObj.contributionLength = countOfContribution
        for contribution in userOrgObj.contributions:
            print 'contribution.myWeight'+str(contribution.myWeight)
        return userOrgObj
    
    
class OrganizationTokenExistsResource(Resource):
    def get(self,tokenName):
        orgObj = session.query(cls.Organization).filter(cls.Organization.token_name == tokenName).first()
        if not orgObj:
            return {"tokenAlreadyExist":"false"}
        else:
             return {"tokenAlreadyExist":"true"}
         
class ChannelOrganizationExistsResource(Resource):
    def get(self,channelId,slackTeamId,userId):
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).filter(cls.Organization.channelId == channelId).first()
        if not orgObj:
            return {"channleOrgExists":"false"}
        else:
            userOrgObj = session.query(cls.UserOrganization).filter(cls.UserOrganization.user_id == userId).filter(cls.UserOrganization.organization_id == orgObj.id).first()
            return {"channleOrgExists":"true","userOrgId":userOrgObj.id,"orgId":orgObj.id,"channelName":orgObj.channelName}    
         
class OrganizationCodeExistsResource(Resource):
    def get(self,code):
        orgObj = session.query(cls.Organization).filter(cls.Organization.code == code).first()
        if not orgObj:
            return {"codeAlreadyExist":"false"}
        else:
             return {"codeAlreadyExist":"true"} 
         
class MemberOranizationsResource(Resource):
    @marshal_with(org_fields)
    def get(self,slackTeamId):
        orgObjs = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).all()
        return  orgObjs
              
    
class OrganizationResource(Resource):
    
    @marshal_with(userOrganization_fields)
    def post(self):
        json = request.json
        orgObj = session.query(cls.Organization).filter(cls.Organization.code == json['code']).first()
        if orgObj:
            return {"codeExist":"true"}
        
        orgObj = session.query(cls.Organization).filter(cls.Organization.token_name == json['token_name']).first()
        if orgObj:
            return {"tokenExist":"true"}
        
        
        #channelId = createChannel(json['channelName'])
        jsonStr = {"token_name":json['token_name'],
                    "slack_teamid":json['slack_teamid'],"a":json['a'],"b":json['b'],
                    "name":json['name'],"code":json['code'],"channelName":json['channelName'],"channelId":json['channelId']}
        userOrgObj = cls.UserOrganization(jsonStr,session)        
        organization = cls.Organization(jsonStr,session)
        session.add(organization)
        session.flush()            
        createUserAndUserOrganizations(organization.id,json['contributers'],json['token'],json['b'],json['access_token'])
        session.commit()        
        orgs = session.query(cls.Organization).filter(cls.Organization.slack_teamid == organization.slack_teamid).all()
        orgChannelId = ''
        count = 1
        for org in orgs:
            if count == 1:
                orgChannelId = org.channelId
            else:
                orgChannelId = orgChannelId + ','+ org.channelId
            count = count + 1;
        userOrgObj.channelId = orgChannelId

        return userOrgObj, 201
    
    def delete(self, id):
        orgObj = session.query(cls.Organization).filter(cls.Organization.id == id).first()
        if orgObj :
            userOrganizationObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == id).all()
            for userOrganization in userOrganizationObjects :
                contributionObjects = session.query(cls.Contribution).filter(cls.Contribution.users_organizations_id == userOrganization.id).all()
                for contributionObject in contributionObjects:                    
                    for contributer in contributionObject.contributionContributers:
                        session.delete(contributer)
                    for bid in contributionObject.bids:
                        session.delete(bid)
                    session.delete(contributionObject)
                session.delete(userOrganization)        
            session.delete(orgObj)
            session.commit()
        return {}, 204
    
def getSlackUsers(access_token):
    print 'access_token'+access_token
    team_users_api_url = 'https://slack.com/api/users.list'
    headers = {'User-Agent': 'DEAP'}
    r = requests.get(team_users_api_url, params={'token':access_token}, headers=headers)
    users = json.loads(r.text)['members']
    print 'slack users:'+str(users)
    return users

    
class getAllSlackUsersResource(Resource):
    def post(self):
        print 'comes here'
        json = request.json
        access_token = json['access_token']
        userIds = json['userIds']
        searchString = json['searchString']
        
        users = getSlackUsers(access_token)
        usersJson = []
        userIdsList = []
        if userIds != '':
            userIdsList = userIds.split(",")
        
        for user in users :
            realName = user['profile']['real_name']
            slackUserId = user['id']
            userName= user['name']
            if user['deleted'] == True :
                continue
            if user['is_bot'] == True :
                continue
            if searchString != '':
                if  searchString  not in realName and searchString  not in userName:
                    continue
            if len(userIdsList) > 0 :
                if slackUserId in userIdsList:   
                    continue
            jsonStr = {"id":user['id'],"name":user['name'],"url":user['profile']['image_48'],"real_name":user['profile']['real_name']}
            usersJson.append(jsonStr)
        return usersJson
    
def createChannel(channelName):
        team_users_api_url = 'https://slack.com/api/channels.create'
        headers = {'User-Agent': 'DEAP'}
        r = requests.post(team_users_api_url, params={'token':g.access_token,'name':channelName}, headers=headers)
        channelObj = json.loads(r.text)
        print str(channelObj)
        
        channelId = ''
        errorText = ''
        try:
            errorText = channelObj['error']
        except KeyError:
            errorText = ''   
        if errorText == '' :
            try:
                channelId = channelObj['channel']['id']
            except KeyError:
                channelId = ''
        else :
            channelId = 'name_taken'
        
        print 'channelId is'+channelId
        return channelId 
        
        
    
def createUserAndUserOrganizations(organizaionId,contributers,token,b,access_token):
    
    usersInSystem = session.query(cls.User).all()
    contributionDic = {}
    for contributer in contributers :
        contributionDic[contributer['contributer_id']] = (float(token)/100)*float(contributer['contributer_percentage'])
    usersDic = {}
    currentUser = '';
    for u in usersInSystem:
        if u.id == g.user_id:
            currentUser = u
        usersDic[u.name] = u.id
    # parse response:
    users = getSlackUsers(access_token)
    print 'slack users:'+str(users)
    for user in users :
        token = 0
        repuation = 0
        try:
            token = contributionDic[user['id']]
            repuation = (int(token))*10/pow(10,(int(b)/50)) 
        except KeyError:
            token = 0
            repuation = 0
        userId = ''
        if user['deleted'] == True :
            continue
        if user['is_bot'] == True :
            continue
        try:
            userId = usersDic[user['name']]
        except KeyError:
            userId = ''
        if userId  == g.user_id :
            currentUser.url = user['profile']['image_48']
            currentUser.url72 = user['profile']['image_72']
            currentUser.real_name = user['profile']['real_name']
            currentUser.slackId = user['id']
            session.add(currentUser)
        if userId == '':            
            jsonStr = {"name":user['name'],"slackId":user['id'],"url":user['profile']['image_48'],"url72":user['profile']['image_72'],"real_name":user['profile']['real_name']}
            u = cls.User(jsonStr,session)
            session.add(u) 
            session.flush() 
            userId = u.id
                         
        jsonStr = {"user_id":userId,
                    "organization_id":organizaionId,
                    "org_tokens":token,
                    "org_reputation":repuation
                    }
        userOrganization = cls.UserOrganization(jsonStr,session)
        session.add(userOrganization)    
    
  
    
def allContributionsFromUser(): 
    users_api_url = 'https://slack.com/api/auth.test'

    params = {
        'access_token': request.form['token'],
    }

    access_token = params["access_token"]

    headers = {'User-Agent': 'DEAP'}
    print 'access_token:'+str(access_token)

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params={'token':access_token}, headers=headers)
    profile = json.loads(r.text)
    print 'slack profile:'+str(profile)  
    contribitions = [];
    milestones = [];
    user = session.query(cls.User).filter(cls.User.name == profile['user']).first()
    if not user:
        return []    
    bidsList = session.query(cls.Bid).filter(cls.Bid.owner == user.id).all()
    mileStonebidsList = session.query(cls.MileStoneBid).filter(cls.MileStoneBid.owner == user.id).all()    
    for bid in bidsList:
        contribitions.append(bid.contribution_id)
    for bid in mileStonebidsList:
        milestones.append(bid.milestone_id)
    jsonString = {'contribitions':contribitions,'milestones':milestones}
    return jsonString


def allChannelIdsForTeam(): 
    slackTeamId = request.form['team']
    orgs = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).all()
    orgChannelId = ''
    count = 1
    for org in orgs:
            if count == 1:
                orgChannelId = org.channelId
            else:
                orgChannelId = orgChannelId + ','+ org.channelId
            count = count + 1;
    return orgChannelId

def showreservetokens(): 
    slackTeamId = request.form['team_id']
    channelId = request.form['channel_id']
    print 'slackTeamId is'+str(slackTeamId)
    print 'channelId is'+str(channelId)
    if(slackTeamId != '' and  channelId != ''):
        orgObj = session.query(cls.Organization).filter(cls.Organization.slack_teamid == slackTeamId).filter(cls.Organization.channelId == channelId).first()
    if not orgObj:
            return "No Project Exists"
    else:
           return 'Reserved Token for this channel is: '+str(orgObj.reserveTokens)
    



class MileStoneResource(Resource):
    @marshal_with(milestone_fields)
    def get(self, id):
        milestoneObject = session.query(cls.MileStone).filter(cls.MileStone.id == id).first()
        print 'got Get for MileStone fbid:'+id
        if not milestoneObject:
            abort(404, message="MileStone {} doesn't exist".format(id))
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == milestoneObject.userOrganization.organization_id).all()
        usersReputationDic = {}
        for userOrgObject in userOrgObjects:
            usersReputationDic[userOrgObject.user_id]=userOrgObject.org_reputation
        totalContributions = 0
        totalContributers = 0
        for milestoneContributer in milestoneObject.milestoneContributers:
            totalContributers = totalContributers + 1 
            milestoneContributer.name= getUser(milestoneContributer.contributer_id).name
            milestoneContributer.real_name= getUser(milestoneContributer.contributer_id).real_name
            milestoneContributer.url= getUser(milestoneContributer.contributer_id).url
        milestoneObject.current_org_id = milestoneObject.userOrganization.organization_id
        milestoneObject.channelName = milestoneObject.userOrganization.organization.channelName
        milestoneObject.code = milestoneObject.userOrganization.organization.code
        milestoneObject.tokenName = milestoneObject.userOrganization.organization.token_name
        for milestoneContribution in milestoneObject.milestoneContributions:
            countOfLines = 0
            shortDescription = '';
            milestoneContributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == milestoneContribution.contribution_id).first()
            for line in milestoneContributionObject.file.splitlines():
                countOfLines = countOfLines + 1
                if(shortDescription != ''):
                    shortDescription = shortDescription  + '\n'
                shortDescription = shortDescription + line
                if countOfLines == 3 :
                    shortDescription = shortDescription + '....'
                    break    
                   
            totalContributions = totalContributions + 1 
            contributionContributersObjs =milestoneContributionObject.contributionContributers
            finalCountOfContribures = 0
            for contributionContributersObj in contributionContributersObjs:
                finalCountOfContribures = finalCountOfContribures + 1
                contributionContributersObj.reputation = usersReputationDic[contributionContributersObj.contributer_id]                
            contributionContributersObjs.sort(key=lambda x: x.reputation, reverse=True)
            totalCountOfContrbuters = 0
            milestoneContribution.contributers = []
            for contributionContributersObj in contributionContributersObjs:
                totalCountOfContrbuters = totalCountOfContrbuters +1
                contributionContributersObj.memberId = getUser(contributionContributersObj.contributer_id).slackId
                contributionContributersObj.url = getUser(contributionContributersObj.contributer_id).url
                milestoneContribution.contributers.append(contributionContributersObj)
                print 'contributionContributersObj.reputation'+str(contributionContributersObj.reputation)
                if totalCountOfContrbuters == 8 :
                    break
            milestoneContribution.remainingContributers = finalCountOfContribures - totalCountOfContrbuters
            milestoneContribution.title= milestoneContributionObject.title
            milestoneContribution.date= milestoneContributionObject.time_created
            milestoneContribution.description = shortDescription
            currentValuation = 0
            last_bid = None
            for bid in milestoneContributionObject.bids:
                last_bid = bid
            if (last_bid):
                currentValuation = last_bid.contribution_value_after_bid
            milestoneContribution.valuation = currentValuation
        milestoneObject.contributions = totalContributions
        milestoneObject.contributers = totalContributers
        return milestoneObject

    def delete(self, id):
        milestoneObject = session.query(cls.MileStone).filter(cls.MileStone.id == id).first()
        if not milestoneObject:
            abort(404, message="MileStone {} doesn't exist".format(id))
        for milestoneContributer in milestoneObject.milestoneContributers:
            session.delete(milestoneContributer)
        for milestoneBid in milestoneObject.milestoneBids:
            session.delete(milestoneBid)
        for milestoneContribution in milestoneObject.milestoneContributions:
            session.delete(milestoneContribution)
        session.delete(milestoneObject)
        session.commit()
        return {}, 204
    
    @marshal_with(milestone_fields)   
    def post(self):          
        parsed_args = milestoneParser.parse_args()  
        milestone = cls.MileStone()
        milestone.owner = parsed_args['owner']
        milestone.description = parsed_args['description']
        milestone.title = parsed_args['title']
        milestone.users_organizations_id = parsed_args['users_organizations_id']
        milestone.destination_org_id = parsed_args['evaluatingTeam']
        session.add(milestone)
        session.flush()
        totalContributions = 0
        totalValue = 0
        totalTokens = 0            
        userOrgObjectForOwner = session.query(cls.UserOrganization).filter(cls.UserOrganization.id == parsed_args['users_organizations_id']).first()
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).all()
        for userOrgObject in userOrgObjects:
            totalTokens = totalTokens + userOrgObject.org_tokens
            userOrgObject.org_tokens = 0
            session.add(userOrgObject)
            
        milestone.tokens = totalTokens
        userObj = getUser(milestone.owner) 
               
        if not userObj:
            abort(404, message="User who is creating milestone {} doesn't exist".format(milestone.owner))    
        allContributionObjects = session.query(cls.Contribution).filter(cls.Contribution.status == 'Open').filter(cls.Contribution.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == userOrgObjectForOwner.organization_id).all()
        contributersDic = {}
        
        for contribution in allContributionObjects:
            totalContributions = totalContributions + 1 
            last_bid = None
            currentValuation = 0
            for bid in contribution.bids:
                last_bid = bid
            if (last_bid):
                currentValuation = last_bid.contribution_value_after_bid
            totalValue = totalValue + currentValuation             
            mileStoneContribution = cls.MileStoneContribution()
            contributionContributersObjs = contribution.contributionContributers
            for contributionContributersObj in contributionContributersObjs:
                try:
                    contributerPercentage = contributersDic[contributionContributersObj.contributer_id]
                except KeyError:
                    contributerPercentage = 0
                contributerPercentage = contributerPercentage + contributionContributersObj.contributer_percentage
                contributersDic[contributionContributersObj.contributer_id] = contributerPercentage
            mileStoneContribution.contribution_id = contribution.id
            mileStoneContribution.milestone_id = milestone.id
            
            milestone.milestoneContributions.append(mileStoneContribution) 
            contribution.status='Closed'
            session.add(contribution)
         
        milestone.contributions =  totalContributions
        milestone.totalValue =  totalValue
        for key, elem in contributersDic.items():
            mileStoneContributer = cls.MileStoneContributer()
            mileStoneContributer.milestone_id = milestone.id
            mileStoneContributer.contributer_id = key
            mileStoneContributer.contributer_percentage = elem/totalContributions
            
            milestone.milestoneContributers.append(mileStoneContributer)
                    
        session.commit()        
        return milestone, 201
    
    
    
class OrganizationCurrentStatusResource(Resource):
    @marshal_with(milestone_fields)
    def get(self, orgId):
        milestone = cls.MileStone()
        totalTokens = 0
        userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == orgId).all()
        usersReputationDic = {}
        orgObject = session.query(cls.Organization).filter(cls.Organization.id == orgId).first()
        for userOrgObject in userOrgObjects:
            totalTokens = totalTokens + userOrgObject.org_tokens
            usersReputationDic[userOrgObject.user_id]=userOrgObject.org_reputation
        milestone.tokens = totalTokens
        milestone.code = orgObject.code
        milestone.tokenName = orgObject.token_name
        milestone.channelName = orgObject.channelName
        allContributionObjects = session.query(cls.Contribution).filter(cls.Contribution.status == 'Open').filter(cls.Contribution.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == orgId).all()
        contributersDic = {}
        totalContributions = 0
        totalContributers = 0
        totalValue = 0
        for contribution in allContributionObjects:
            shortDescription = ''
            countOfLines = 0
            for line in contribution.file.splitlines():
                countOfLines = countOfLines + 1
                if(shortDescription != ''):
                    shortDescription = shortDescription  + '\n'
                shortDescription = shortDescription + line
                if countOfLines == 3 :
                    shortDescription = shortDescription + '....'
                    break
            totalContributions = totalContributions + 1 
            last_bid = None
            currentValuation = 0
            for bid in contribution.bids:
                last_bid = bid
            if (last_bid):
                currentValuation = last_bid.contribution_value_after_bid
            
            totalValue = totalValue + currentValuation             
            mileStoneContribution = cls.MileStoneContribution()
            mileStoneContribution.valuation = currentValuation
            mileStoneContribution.description = shortDescription
            contributionContributersObjs = contribution.contributionContributers
            finalCountOfContribures = 0
            for contributionContributersObj in contributionContributersObjs:
                finalCountOfContribures = finalCountOfContribures + 1
                contributionContributersObj.reputation = usersReputationDic[contributionContributersObj.contributer_id]
                try:
                    contributerPercentage = contributersDic[contributionContributersObj.contributer_id]
                except KeyError:
                    contributerPercentage = 0
                contributerPercentage = contributerPercentage + contributionContributersObj.contributer_percentage
                contributersDic[contributionContributersObj.contributer_id] = contributerPercentage
            contributionContributersObjs.sort(key=lambda x: x.reputation, reverse=True)
            totalCountOfContrbuters = 0
            mileStoneContribution.contributers = []
            for contributionContributersObj in contributionContributersObjs:
                totalCountOfContrbuters = totalCountOfContrbuters +1
                contributionContributersObj.memberId = getUser(contributionContributersObj.contributer_id).slackId
                contributionContributersObj.url = getUser(contributionContributersObj.contributer_id).url
                mileStoneContribution.contributers.append(contributionContributersObj)
                print 'contributionContributersObj.reputation'+str(contributionContributersObj.reputation)
                if totalCountOfContrbuters == 8 :
                    break
            mileStoneContribution.remainingContributers = finalCountOfContribures - totalCountOfContrbuters
            mileStoneContribution.contribution_id = contribution.id
            mileStoneContribution.title= contribution.title
            mileStoneContribution.date= contribution.time_created
            milestone.milestoneContributions.append(mileStoneContribution) 
         
        milestone.contributions =  totalContributions
        milestone.totalValue =  totalValue
        for key, elem in contributersDic.items():
            totalContributers = totalContributers + 1
            mileStoneContributer = cls.MileStoneContributer()
            mileStoneContributer.contributer_id = key
            mileStoneContributer.contributer_percentage = elem/totalContributions
            mileStoneContributer.name= getUser(mileStoneContributer.contributer_id).name
            mileStoneContributer.real_name= getUser(mileStoneContributer.contributer_id).real_name
            mileStoneContributer.url= getUser(mileStoneContributer.contributer_id).url
            milestone.milestoneContributers.append(mileStoneContributer)
        milestone.contributers = totalContributers
        return milestone


class AllMileStonesForOrgResource(Resource):
    def get(self, id):
        allMileStoneObjects = session.query(cls.MileStone).filter(cls.MileStone.users_organizations_id == cls.UserOrganization.id).filter(cls.UserOrganization.organization_id == id).all()
        mileStonesJson = []
        for milestone in allMileStoneObjects:
            jsonStr = {"id":milestone.id,"title":milestone.title}
            mileStonesJson.append(jsonStr)
        return mileStonesJson