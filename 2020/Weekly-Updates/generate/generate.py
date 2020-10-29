from os.path import dirname, abspath, join
import json

import jinja2

GEN_INDEX = 7
UP_ARROW = 'https://upload.wikimedia.org/wikipedia/commons/f/fe/Green-Up-Arrow.svg'
DOWN_ARROW = 'https://upload.wikimedia.org/wikipedia/commons/6/62/RedDownArrow.svg'

class Generator(object):

    def __init__(self):
        self.dir_path = dirname(abspath(__file__))
        self.data = json.loads(self.load_data("data.json"))
        self.week = self.data[GEN_INDEX]
        self.template = self.load_data("template.txt")
        self.calculate()
        self.markdown = self.render()
        self.write()

    def load_data(self, file_name):
        with open(join(self.dir_path, file_name), 'r') as data_file:
            return data_file.read()

    def write(self):
        file_name = "Week%i.md" % GEN_INDEX
        with open(join(dirname(self.dir_path), file_name), 'w') as output_file:
            output_file.write(self.markdown)

    def render(self):
        return jinja2.Environment().from_string(self.template).render(
            week=self.week,
            index=GEN_INDEX
        )

    def calculate(self):
        results_dict = {
            index: x.get("Results", [])
            for index, x in enumerate(self.data) if index > 0 and index <= GEN_INDEX
        }

        for rank in self.week.get("PowerRankings", {}).get("Ranks", []):
            team_name = rank["Team"]
            rank["Metadata"] = self.get_team_data(team_name, results_dict)
            rank["Metadata"]["Change"] = self.get_change(team_name)

    def get_change(self, team_name):
        previous_powers = [
            x.get("PowerRankings", None) for index, x in enumerate(self.data)
            if x.get("PowerRankings") and index < GEN_INDEX
        ]
        if not previous_powers:
            return "--"
        previous_power = previous_powers[-1]
        previous_rank = [
            index for index, x in enumerate(previous_power["Ranks"]) if x["Team"] == team_name
        ][0]

        current_power = self.week["PowerRankings"]
        current_rank = [
            index for index, x in enumerate(current_power["Ranks"]) if x["Team"] == team_name
        ][0]

        if current_rank == previous_rank:
            return "--"
        if current_rank < previous_rank:
            return "<img src='%s' width='15px'> %i" % (UP_ARROW, previous_rank - current_rank)
        return "<img src='%s' width='15px'> %i" % (DOWN_ARROW, current_rank - previous_rank)


    @staticmethod
    def get_team_data(team_name, results_dict):

        team_results = [
            x for x in
            [j for i in (results_dict[key] for key in sorted(results_dict.keys())) for j in i]
            if team_name in x.keys()
        ]
        recent = 3
        recent_length = len(team_results[-recent:])

        metadata = {}
        metadata["Wins"] = len([
            x for x in team_results
            if x[team_name] == max(x.values()) and max(x.values()) != min(x.values())
        ])
        metadata["Losses"] = len([
            x for x in team_results
            if x[team_name] == min(x.values()) and max(x.values()) != min(x.values())
        ])
        metadata["Ties"] = len([
            x for x in team_results
            if max(x.values()) == min(x.values())
        ])
        metadata["Record"] = "%i-%i-%i" % (metadata["Wins"], metadata["Losses"], metadata["Ties"])
        metadata["Points"] = round(sum([
            x[team_name] for x in team_results
        ]), 2)
        metadata["PointsAvg"] = round(metadata["Points"] / len(team_results), 2)
        metadata["PointsAgainst"] = round(sum([
            value for x in team_results
            for (key, value) in x.items() if key.lower() != team_name.lower()
        ]), 2)
        metadata["PointsAgainstAvg"] = round(metadata["PointsAgainst"] / len(team_results), 2)

        metadata["WinsLast3"] = len([
            x for x in team_results[-recent:]
            if x[team_name] == max(x.values()) and max(x.values()) != min(x.values())
        ])
        metadata["LossesLast3"] = len([
            x for x in team_results[-recent:]
            if x[team_name] == min(x.values()) and max(x.values()) != min(x.values())
        ])
        metadata["TiesLast3"] = len([
            x for x in team_results[-recent:]
            if max(x.values()) == min(x.values())
        ])
        metadata["RecordLast3"] = "%i-%i-%i" % (metadata["WinsLast3"], metadata["LossesLast3"], metadata["TiesLast3"])
        metadata["PointsAvgLast3"] = round(sum([
            x[team_name] for x in team_results[-recent:]
        ]) / recent_length, 2)

        metadata["PointsAgainstAvgLast3"] = round(sum([
            value for x in team_results[-recent:]
            for (key, value) in x.items() if key.lower() != team_name.lower()
        ]) / recent_length, 2)

        return metadata






if __name__ == '__main__':
    Generator()
