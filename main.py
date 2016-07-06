__author__ = 'Sergei Wallace'

from xml.etree.ElementTree import *
from sys import argv


class Home:
    def __init__(self, root_index, root):
        self._obstructions = []

        for child in root[root_index]:
            if child.tag == 'House':
                self._house = (float(child[0].text), float(child[1].text), float(child[2].text))

            elif child.tag == 'PropertyLine':
                self._property_line = (float(child[0].text), float(child[1].text), float(child[2].text))
            else:
                obstruction = (float(child[0].text), float(child[1].text), float(child[2].text))
                self._obstructions.append(obstruction)

        print("property line:", self._property_line)
        print("house address:", root[root_index].get('addr'))
        self._shadows = []
        self.find_shadows()

        self.find_merged_shadows()

        self._sight_line = []

        print("shadow:", self._shadows)
        self.find_sight_line()


        self.max_sight_line = self.largest_sight_line()

    def shadow(self, obstruction):
        house_x1, house_x2, house_y = self._house[0], self._house[1], self._house[2]
        obs_x1, obs_x2, obs_y = obstruction[0], obstruction[1], obstruction[2]
        shad_y = self._property_line[2]
        if (obs_x1 - house_x2) == 0:
            shad_x1 = house_x2
        if (obs_x1 - house_x2) != 0:
            slope2 = (obs_y - house_y) / (obs_x1 - house_x2)
            shad_x1 = (shad_y - house_y) / slope2 + house_x2
        if (obs_x2 - house_x1) == 0:
            shad_x2 = house_x1
        if (obs_x2 - house_x1) != 0:
            slope1 = (obs_y - house_y) / (obs_x2 - house_x1)
            shad_x2 = (shad_y - house_y) / slope1 + house_x1
        if shad_x1 < self._property_line[0]:
            shad_x1 = self._property_line[0]
        if shad_x2 > self._property_line[1]:
            shad_x2 = self._property_line[1]

        shadow = (round(shad_x1, 3), round(shad_x2, 3), shad_y)
        return shadow


    def merge_shadow(self, shadow_a, shadow_b):
        if shadow_a[1] < shadow_b[0] or shadow_a[0] > shadow_b[1]:
            shadow = None
        if shadow_a[0] <= shadow_b[0] <= shadow_a[1]:
            if shadow_b[1] <= shadow_a[1]:
                shadow = (shadow_a[0], shadow_a[1], shadow_a[2])

            else:
                shadow = (shadow_a[0], shadow_b[1], shadow_a[2])

        elif shadow_a[0] <= shadow_b[1] <= shadow_a[1]:
            shadow = (shadow_b[0], shadow_a[1], shadow_a[2])

        elif shadow_b[0] <= shadow_a[0] <= shadow_b[1]:
            if shadow_a[1] <= shadow_b[1]:
                shadow = (shadow_b[0], shadow_b[1], shadow_a[2])

            else:
                shadow = (shadow_b[0], shadow_a[1], shadow_a[2])

        elif shadow_b[0] <= shadow_a[1] <= shadow_b[1]:
            shadow = (shadow_a[0], shadow_b[1], shadow_a[2])

        return shadow, shadow_a, shadow_b

    def find_shadows(self):
        for obstruction in self._obstructions:
            # print("obstruction =", obstruction)
            self._shadows.append(self.shadow(obstruction))
        #sort the merged shadows list in order of x1
        self._shadows = sorted(self._shadows, key=lambda x: x[0])

    def find_merged_shadows(self):
        i = 0
        while i < len(self._shadows) - 1:
            j = i + 1
            while j < len(self._shadows):
                merged_shadow, old_shadow1, old_shadow2 = self.merge_shadow(self._shadows[i], self._shadows[j])
                if merged_shadow is None:
                    j += 1
                else:
                    self._shadows.insert(i, merged_shadow)
                    self._shadows.remove(old_shadow1)
                    self._shadows.remove(old_shadow2)
                    j = i + 1
            i += 1

        #sort the merged shadows list in order of x1
        self._shadows = sorted(self._shadows, key=lambda x: x[0])

    def find_sight_line(self):
        if self._shadows:
            #check if there is a sight line at the left most point of the property line
            if self._property_line[0] < self._shadows[0][0]:
                self._sight_line.append((self._property_line[0], self._shadows[0][0], self._property_line[2]))

            for i in range(len(self._shadows) - 1):
                self._sight_line.append((self._shadows[i][1], self._shadows[i+1][0], self._property_line[2]))

            #check if there is a sight line at the right most point of the property line
            if self._property_line[1] > self._shadows[-1][1]:
                self._sight_line.append((self._shadows[-1][1], self._property_line[1], self._property_line[2]))


    def largest_sight_line(self):
        lengths = []
        if self._sight_line:
            for line in self._sight_line:
                length = line[1] - line[0]
                lengths.append(length)

        if not lengths:
            return "No View"
        return round(max(lengths), 4)




def main():
    tree = ElementTree()
    tree.parse(argv[1])
    root = tree.getroot()

    test_results = Element('TestResults')
    #test_results.text = "\n\t"
    homes = []
    i = 0
    for child in root:
        home = Home(i, root)
        homes.append(home)
        test = SubElement(test_results, 'Test')
        test.set('addr', child.get('addr'))
        test.text = str(home.largest_sight_line())
        print()
        i += 1

    tree = ElementTree(test_results)
    tree.write(argv[2])

if __name__ == "__main__":
    main()