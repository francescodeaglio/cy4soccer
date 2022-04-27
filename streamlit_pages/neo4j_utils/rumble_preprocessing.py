"""
!!!!OLD!!! See the rumble_preprocessing notebook instead.

Preprocessing of StatsBomb data made in Rumble/Jsoniq

To run it, you need to launch RumbleDb on the port 8001

spark-submit rumbledb-1.16.2-for-spark-3.1.jar --server yes --port 8001

In the same folder of rumbledb-1.16.2-for-spark-3.1.jar (from which the script is launched)
you need to store gamenumber.json and gamenumber_events.json
See RumbleDb documentation online
"""

import requests
import json
import time


def rumble(line, query, server, outfilename):
    start = time.time()
    response = json.loads(requests.post(server, data=query, params={"result-size": 1000}).text)
    end = time.time()
    print("Took: %s s" % (end - start))
    if 'warning' in response:
        print(json.dumps(response['warning']))
    if 'values' in response:
        if not outfilename:
            for e in response['values']:
                print(json.dumps(e))
                print()
        if outfilename:
            with open(outfilename, 'w') as outfile:
                json.dump(response['values'], outfile)
    elif 'error-message' in response:
        return response['error-message']
    else:
        return response


def preprocess_lineups(gamenumber, team):
    server = 'http://localhost:8001/jsoniq'

    rumble_preprocess_lineups = \
    """
    let $players := for $doc in json-doc(\"""" + gamenumber + """.json")
    for $team in $doc[]
    where $team.team_name eq \""""+team+"""\"
    for $player in $team.lineup[]
    for $pos in $player.positions[]
    return {"name":$player.player_name,
            "jersey_number":$player.jersey_number,
            "cards":$player.cards
            , "pos" : $pos}

    let $a:=[for $player in $players
    return {"name":$player.name,
        "jersey_number":$player.jersey_number,
        "cards":$player.cards,
        "start" : $player.pos.from,
        "end" : $player.pos.to,
        "pos" : $player.pos}]

    let $multiple:=for $p in $a[]
    group by $pl:=$p.name
    where count($p.name) gt 1
    let $all := {"name" : $p.name,
            "jersey_number":$p.jersey_number,
            "cards":$p.cards,
            "start" : $p.start,
            "end": $p.end,
            "pos" : $p.pos}
    for $x in $all
    return {
        "name": $x.name[[1]],
        "jersey_number":$x.jersey_number[[1]],
        "cards":$x.cards[[1]],
        "start" : $x.start[[1]],
        "end" : $x.end[[count($p.name)]],
        "pos" : $x.pos[[1]]}

    let $single := for $p in $a[]
    group by $pl:=$p.name
    where count($p.name) eq 1
    return $p

    let $starters := for $p in ($single, $multiple)
    where $p.pos.start_reason eq "Starting XI"
    return {"name" : $p.name,
            "jersey_number":$p.jersey_number,
            "cards":$p.cards,
            "start" : $p.start,
            "end": $p.end,
            "starting" : true}

    let $notstarters :=for $p in ($single, $multiple)
    where $p.pos.start_reason ne "Starting XI"
    return {"name" : $p.name,
            "jersey_number":$p.jersey_number,
            "cards":$p.cards,
            "start" : $p.start,
            "end": $p.end,
            "starting" : false}

    return ($notstarters, $starters)""".replace("\n", " ")



    rumble(rumble_preprocess_lineups, rumble_preprocess_lineups, server, "lineup_"+team+".json")

def preprocess_passes(gamenumber, team):
    server = 'http://localhost:8001/jsoniq'

    rumble_preprocess_passes = """
let $beg := for $doc in json-doc(\""""+gamenumber+"""_events.json")
for $x in $doc[]
count $c
where $x."type".name eq "Pass" and $x.possession_team.name eq \""""+team+"""" and $x.team.name eq \""""+team+""""
where $x.pass.recipient.name
return { "from" : $x.player.name, "to":$x.pass.recipient.name, "possession" : $x.possession, "length": $x.pass.length, "angle": 
        $x.pass.angle, "height":$x.pass.height.name, "timestamp": $x.timestamp, "pattern" : $x.play_pattern.name, 
 "body_part":$x.pass.body_part.name, "period": $x.period
}


for $e in $beg
group by $p:=$e.possession
for $x in $e
order by $x.period, $x.timestamp
count $c
return { "from" : $x.from, "to":$x.to, "possession" : $x.possession, "length": $x.length, "angle": 
        $x.angle, "height":$x.height, "timestamp": $x.timestamp, "pattern" : $x.pattern, "order": $c, 
 "body_part":$x.body_part, "period":$x.period
}
    
    
    """


    rumble(rumble_preprocess_passes, rumble_preprocess_passes, server, "passes_"+team+".json")
