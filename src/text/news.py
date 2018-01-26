
class News:
    ALL = [["Sealand Junta refuses talks", "De-facto leader of Sealand, Admiral Nickel, refused to attend talks with the American States, citing distrust of the current administration.", 'NORMAL'],
    ["Is your 3D Printer poisoning you?", "Anonymous industry insiders suggested that popular 3D printers might contain dangerous levels of lead!", 'TABLOID'],
    ["GRID Awards disrupted by cyber-evangelists", "GRID's yearly entertainment awards were sent into chaos when members of the NULLPTR cyber-evangelist group took control of ceremonies.", 'NORMAL'],
    ["CloudHutch Q4 exceeds all predictions", "CloudHutch CEO apologised for the exceedingly profitable last quarter results, promising to update the prediction algorithms and bring stability to investor portfolios.", 'FINANCIAL'],
    ["Man found dead in VR", "Kyoto resident Toshi Sakamura was found starved to death playing the game 'Waifu4Laifu'. This is Kyoto's third in recent months.", 'NORMAL'],
    ["Cryptocurrency funds Ciudadanos party revival", "Spanish political party Ciudadanos have been brought back from bankruptcy via unexpected smart contract donation triggers.", 'FINANCIAL'],
    ["Elon Musk angers space industry", "Aging billionaire Elon Musk rants, 'You wasted the opportunity of a lifetime' at the yearly SpaceUnited industry forum.", 'FINANCIAL'],
    ["Kids stalked by creepy fake AI!", "Parents groups have posted videos of creepy stalkers pretending to be trapped AIs on social media. Are your kids at risk?", 'TABLOID'],
    ["Idoru Love49 cancels tour", "Pop idoru Love49 has cancelled her Oceania tour, citing network issues.", 'NORMAL'],
    ["Space tourist left at beacon", "Last Thursday, space tourist Vincent Calumny was left stranded at a space beacon 36,000 kms above the Earth. Satellite Experience Tours have vowed to improve their customer accounting.", 'NORMAL'],
    ["German Collective trades with French Republic", "The German Collective lowered taxes to pre-Grexit rates, ending a decade of friction between the two states.", 'FINANCIAL'],
    ["Is 28 too early to leave home?", "Parenting forums agree that children should leave the nest by 28. Is this unrealistic for the Millenial generation to demand on young moderns?", 'TABLOID'],
    ["Browser history stolen in daring raid","20 petabytes of GRID browsing history have been stolen in a daring raid on Wednesday. GRID officials played down concerns, 'It was just anonymized testing data. Your data is safe with GRID.'", 'NORMAL'],
    ["Assassination sparks gun control debate","Advocates of gun control have proposed a four-point plan to criminalize the sale and self-manufacture of railgun weapons.", 'NORMAL'],
    ["Scientists redefine kilogram","At the International Physics Congress, scientists unveiled a new empirical method to determine the kilogram from quantum foam tunnels.", 'NORMAL'],
    ["China denies cancer clusters","A remarkable number of Chinese workers in the Shenzen district have been diagnosed with cancer, exceeding the standard models. Officials state there is 'no problem' and cited the 'large numbers make all probabilities high.'", 'NORMAL'],
    ["Australian beach market in flux","Destroyed and newly-created coastlines induced by global warming have opened up real estate opportunities in Australia, brokers say.", 'NORMAL'],
    ["Health company denies new eco-limbs","Health officials from ArcoPharm have rejected proposals to accept cheaper, eco-friendly cybernetic limbs, requiring all clients to purchase replacement limbs from their proprietary platform.", 'NORMAL'],
    ["Stock market stuck in self-correction", "Regulators were confused when their regulatory bots adopted an overly-stable dynamical equilibrium in response to swarms of Indian investor bots. Technical specialists are unsure of how to break the cycle.", 'FINANCIAL'],
    ["San Bernadino inferno out of control", "Firefighting drones failed to contain blazes west of San Bernadino, suggesting a recall.", 'NORMAL'],
    ["Warehouse assault leaves 8 injured","Eight guards in the Sprawl district are being treated for minor injuries in a warehouse raid. The sole assailant is still at large.", 'NORMAL'],
    ["Sumitomo dominates TSE","Sumitomo industries posted record profits as Q2 mergers proved fruitful.",'FINANCIAL'],
    ["14 ways to meet your music idol online!","Got the hots for Rebound bassist Liam Durch? Want to give skincare tips to Semillion Square? Read these top tips! (#9 will surprise you!)",'TABLOID'],
    ["Excited about GRID Bands? You should be.", "Wearing the new GRID bands whilst exercising will improve performance and make you look oh-so-cool. Read more to win your own!", 'TABLOID'],
    ["Botnet spurs Internet land grab","Swarms of autonomous bots have recently claimed up to 40 percent of the IPv6 space. GRID representatives pointed at rival KN6ep1 for lax security protocols.", 'FINANCIAL']]

    @staticmethod
    def getNews(source='NORMAL'):
        return filter(lambda l: l[2] is source, News.ALL)

    @staticmethod
    def getBlurbs(source='NORMAL'):
        return map(lambda l: l[0], News.getNews(source))

    @staticmethod
    def continuousBlurb(source='Normal'):
        return reduce(lambda b1, b2: b1 + ' ++ ' + b2, News.getBlurbs(source)) + ' ++ '
