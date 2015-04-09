# -*- coding: utf-8 -*-

from random import randint, random
from db import DB
from paper import Paper
from problem import Problem
from unit import Unit

fkpcov = 0.5
fdiff = 0.5

def is_contain(paper, problem):
    for i in range(len(problem.points)):
        if problem.points[i] in paper.points:
            return True
    return False

def get_kp_coverage(unit_list, paper):
    for i in range(len(unit_list)):
        kp = []
        for p in unit_list[i].problem_list:
            kp += p.points
        common = list(set(kp).intersection(set(paper.points)))
        unit_list[i].kp_coverage = len(common) * 1.00 / len(paper.points)
    return unit_list

"""
def get_kp_coverage(unit_list, paper):
    for i in range(len(unit_list)):
        each_point_score = [0] * 11
        for p in unit_list[i].problem_list:
            for point in p.points:
                each_point_score[point] += p.score
        result = 0
        for i in range(len(paper.points)):
            result += (1 - abs(each_point_score[paper.points[i]]
                - paper.each_point_score[i]) * 1.00 / paper.each_point_score[i])
        unit_list[i].kp_coverage = result * 1.00 / len(paper.points)
    return unit_list
"""

def get_adaptation_degree(unit_list, paper, fkpcov, fdiff):
    unit_list = get_kp_coverage(unit_list, paper)
    for i in range(len(unit_list)):
        unit_list[i].adaptation_degree = 1 - (1 - unit_list[i].kp_coverage) \
                * fkpcov - abs(unit_list[i].difficulty - paper.difficulty) \
                * fdiff
    return unit_list

def CSZQ(count, paper, problem_list):
    unit_list = []
    each_type_count = paper.each_type_count
    for i in range(count):
        unit = Unit()
        unit.id = i + 1

        while paper.total_score != unit.sum_score:
            unit.problem_list = []
            for j in range(len(each_type_count)):
                one_type_problem = [
                        p for p in problem_list \
                                if p.type == j+1 and is_contain(p, paper)]

                for k in range(1, each_type_count[j] + 1):
                    length = len(one_type_problem)
                    index = randint(0, length - k)
                    unit.problem_list.append(one_type_problem[index])
                    one_type_problem[index], one_type_problem[length-k-1] = \
                            one_type_problem[length-k-1], \
                            one_type_problem[index]

        unit_list.append(unit)

    unit_list = get_kp_coverage(unit_list, paper)
    unit_list = get_adaptation_degree(unit_list, paper, fkpcov, fdiff)
    return unit_list

def select(unit_list, count):
    selected_unit_list = []
    all_adaptation_degree = 0
    for u in unit_list:
        all_adaptation_degree += u.adaptation_degree

    while len(selected_unit_list) != count:
        degree = 0.0
        rand_degree = randint(1, 100) * 0.01 * all_adaptation_degree

        for j in range(len(unit_list)):
            degree += unit_list[j].adaptation_degree
            if degree >= rand_degree:
                if not unit_list[j] in selected_unit_list:
                    selected_unit_list.append(unit_list[j])
                break
    return selected_unit_list

def cross(unit_list, count, paper):
    crossed_unit_list = []
    while (len(crossed_unit_list) != count):
        index_one = randint(0, len(unit_list) - 1)
        index_two = randint(0, len(unit_list) - 1)
        unit_one = Unit()
        unit_two = Unit()
        if index_one != index_two:
            unit_one = unit_list[index_one]
            unit_two = unit_list[index_two]
            cross_position = randint(0, unit_one.problem_count - 2)
            score_one = unit_one.problem_list[cross_position].score + \
                    unit_one.problem_list[cross_position+1].score
            score_two = unit_two.problem_list[cross_position].score + \
                    unit_two.problem_list[cross_position+1].score
            if score_one == score_two:
                unit_new_one = Unit()
                unit_new_one.problem_list += unit_one.problem_list
                unit_new_two = Unit()
                unit_new_two.problem_list += unit_two.problem_list
                for i in range(cross_position, cross_position + 2):
                    unit_new_one.problem_list[i] = unit_two.problem_list[i]
                    unit_new_two.problem_list[i] = unit_one.problem_list[i]
                unit_new_one.id = len(crossed_unit_list)
                unit_new_two.id = unit_new_one.id + 1
                if len(crossed_unit_list) < count:
                    crossed_unit_list.append(unit_new_one)
                if len(crossed_unit_list) < count:
                    crossed_unit_list.append(unit_new_two)

    crossed_unit_list = get_kp_coverage(crossed_unit_list, paper)
    crossed_unit_list = get_adaptation_degree(crossed_unit_list, paper,
            fkpcov, fdiff)
    return crossed_unit_list

def change(unit_list, problem_list, paper):
    index = 0
    for u in unit_list:
        index = randint(0, len(u.problem_list) - 1)
        temp = u.problem_list[index]

        problem = Problem()
        for i in range(len(temp.points)):
            if temp.points[i] in paper.points:
                problem.points.append(temp.points[i])

        other_db = [
                p for p in problem_list \
                        if len(set(p.points).
                            intersection(set(problem.points))) > 0]
        small_db = [
                p for p in other_db \
                        if is_contain(paper, p) and p.score == temp.score \
                        and p.type == temp.type and p.id != temp.id]

        if len(small_db) > 0:
            change_index = randint(0, len(small_db) - 1)
            u.problem_list[index] = small_db[change_index]

    unit_list = get_kp_coverage(unit_list, paper)
    unit_list = get_adaptation_degree(unit_list, paper, fkpcov, fdiff)
    return unit_list

def is_end(unit_list, end_condition):
    if unit_list is not None:
        for i in range(len(unit_list)):
            if (unit_list[i].adaptation_degree >= end_condition):
                return True
    return False

def show_result(unit_list, expand):
    for u in unit_list:
        if u.adaptation_degree >= expand:
            print u"第 %d 套" % u.id
            print u"题目数量\t知识点分布\t难度系数\t适应度"
            print u"%d\t\t%.2f\t\t%.2f\t\t%.2f" % (
                    u.problem_count, u.kp_coverage,\
                            u.difficulty, u.adaptation_degree)

def show_unit(unit_list):
    for u in unit_list:
        print u"试卷编号\t知识点分布\t难度系数\t适应度"
        print u"%d\t\t%.2f\t\t%.2f\t\t%.2f" % (
                u.id, u.kp_coverage, u.difficulty, u.adaptation_degree)
        u.problem_list.sort(key=lambda x:x.id)
        for p in u.problem_list:
            print str(p.id) + "\t",
        print "\n"

class Genetic:
    def __init__(self, paper, db):
        self.paper = paper
        self.db = db

    def run(self, expand):
        count = 1
        run_count = 500
        unit_list = CSZQ(20, self.paper, self.db.problem_db)
        while (not is_end(unit_list, expand)):
            count = count + 1
            if (count > run_count):
                break
            unit_list = select(unit_list, 10)
            unit_list = cross(unit_list, 20, self.paper)
            if (is_end(unit_list, expand)):
                break

            p = random()
            if p < 0.02:
                unit_list = change(unit_list, self.db.problem_db, self.paper)

        if (count <= run_count):
            for u in unit_list:
                if u.adaptation_degree >= expand:
                    return u

    def test_run(self):
        count = 1
        expand = 0.98
        run_count = 500

        unit_list = CSZQ(20, self.paper, self.db.problem_db)
        print u"初始种群:"
        show_unit(unit_list)
        print u"----------迭代开始-----------"

        while (not is_end(unit_list, expand)):
            opt_unit = Unit()
            for i in range(len(unit_list)):
                if opt_unit.adaptation_degree < unit_list[i].adaptation_degree:
                    opt_unit.adaptation_degree = unit_list[i].adaptation_degree
                    opt_unit.difficulty = unit_list[i].difficulty
                    opt_unit.kp_coverage = unit_list[i].kp_coverage

            print u"知识点覆盖率：", opt_unit.kp_coverage
            print u"难度：", opt_unit.difficulty
            print u"最大适应值：", opt_unit.adaptation_degree
            print u"在第 %d 代未得到结果" % count
            print

            count = count + 1
            if (count > run_count):
                print u"失败，请重新设计条件"
                break

            unit_list = select(unit_list, 10)
            unit_list = cross(unit_list, 20, self.paper)

            if (is_end(unit_list, expand)):
                break

            p = random()
            if p < 0.02:
                unit_list = change(unit_list, self.db.problem_db, self.paper)

        if (count <= run_count):
            print u"在第 %d 代得到结果" % count
            print u"期望试卷难度" + str(self.paper.difficulty)
            show_result(unit_list, expand)

def main():
    paper = Paper()

    paper.id = 1
    paper.total_score = 100
    paper.difficulty = 0.52
    paper.points = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    paper.each_point_score = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    paper.each_type_count = [15, 15, 5]
    paper.each_type_score = [30, 30, 40]

    db = DB(paper)
    genetic = Genetic(paper, db)
    genetic.test_run()


if __name__ == '__main__':
    main()
