import unittest
from rag_service.app.core.chains.text2sql import create_sql_agent

class TestText2SQL(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.agent = create_sql_agent()
        self.tools_description = "\n".join([
            f"{tool.name}: {tool.description}"
            for tool in self.agent.tools
        ])

    def test_basic_queries(self):
        """测试基本的SQL查询场景"""
        test_cases = [
            {
                "name": "简单SELECT查询",
                "query": "查询所有用户的姓名和邮箱",
                "expected": "SELECT name, email FROM users;"
            },
            {
                "name": "带WHERE条件的查询",
                "query": "查找年龄大于25岁的用户",
                "expected": "SELECT * FROM users WHERE age > 25;"
            },
            {
                "name": "多表JOIN查询",
                "query": "查询所有用户的订单信息，包括用户名和订单金额",
                "expected": "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id;"
            }
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                result = self.agent.run(
                    query=case["query"],
                    tools=self.tools_description
                )
                self.assertIn(case["expected"], result)

    def test_nested_queries(self):
        """测试嵌套查询场景"""
        test_cases = [
            {
                "name": "子查询在WHERE子句中",
                "query": """
                假设有两个表：
                ```sql
                create table students (id int, name string, class_id int);
                create table classes (id int, name string, teacher_id int);
                create table teachers (id int, name string);
                ```
                查找所有由'张老师'教的学生的姓名
                """,
                "expected": """
                SELECT s.name 
                FROM students s 
                WHERE s.class_id IN (
                    SELECT c.id 
                    FROM classes c 
                    JOIN teachers t ON c.teacher_id = t.id 
                    WHERE t.name = '张老师'
                );
                """
            },
            {
                "name": "子查询在FROM子句中",
                "query": """
                假设有两个表：
                ```sql
                create table orders (id int, user_id int, amount decimal, order_date date);
                create table users (id int, name string);
                ```
                查询每个用户的平均订单金额，并找出高于平均值的用户
                """,
                "expected": """
                SELECT u.name, o.avg_amount
                FROM users u
                JOIN (
                    SELECT user_id, AVG(amount) as avg_amount
                    FROM orders
                    GROUP BY user_id
                ) o ON u.id = o.user_id
                WHERE o.avg_amount > (
                    SELECT AVG(amount)
                    FROM orders
                );
                """
            }
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                result = self.agent.run(
                    query=case["query"],
                    tools=self.tools_description
                )
                self.assertIn(case["expected"], result)

    def test_union_queries(self):
        """测试UNION查询场景"""
        test_cases = [
            {
                "name": "简单UNION查询",
                "query": """
                假设有两个表：
                ```sql
                create table active_users (id int, name string, last_login date);
                create table inactive_users (id int, name string, last_login date);
                ```
                查询所有用户（包括活跃和非活跃）的姓名和最后登录时间
                """,
                "expected": """
                SELECT name, last_login
                FROM active_users
                UNION
                SELECT name, last_login
                FROM inactive_users;
                """
            },
            {
                "name": "UNION ALL查询",
                "query": """
                假设有两个表：
                ```sql
                create table current_employees (id int, name string, salary decimal);
                create table former_employees (id int, name string, salary decimal);
                ```
                查询所有员工（包括现任和前任）的姓名和薪资，保留重复记录
                """,
                "expected": """
                SELECT name, salary
                FROM current_employees
                UNION ALL
                SELECT name, salary
                FROM former_employees;
                """
            }
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                result = self.agent.run(
                    query=case["query"],
                    tools=self.tools_description
                )
                self.assertIn(case["expected"], result)

    def test_complex_queries(self):
        """测试复杂查询场景"""
        test_cases = [
            {
                "name": "复杂嵌套查询",
                "query": """
                假设有三个表：
                ```sql
                create table students (id int, name string, class_id int);
                create table classes (id int, name string, teacher_id int);
                create table scores (student_id int, subject string, score decimal);
                ```
                查询每个班级中，成绩高于该班级平均分的学生姓名和成绩
                """,
                "expected": """
                SELECT s.name, sc.score
                FROM students s
                JOIN scores sc ON s.id = sc.student_id
                JOIN (
                    SELECT c.id as class_id, AVG(sc2.score) as avg_score
                    FROM classes c
                    JOIN students s2 ON c.id = s2.class_id
                    JOIN scores sc2 ON s2.id = sc2.student_id
                    GROUP BY c.id
                ) class_avg ON s.class_id = class_avg.class_id
                WHERE sc.score > class_avg.avg_score;
                """
            },
            {
                "name": "UNION和子查询组合",
                "query": """
                假设有三个表：
                ```sql
                create table current_orders (id int, user_id int, amount decimal, order_date date);
                create table historical_orders (id int, user_id int, amount decimal, order_date date);
                create table users (id int, name string, vip_level int);
                ```
                查询所有VIP用户（vip_level > 0）的订单信息，包括当前和历史订单
                """,
                "expected": """
                SELECT u.name, o.amount, o.order_date
                FROM users u
                JOIN (
                    SELECT user_id, amount, order_date
                    FROM current_orders
                    UNION ALL
                    SELECT user_id, amount, order_date
                    FROM historical_orders
                ) o ON u.id = o.user_id
                WHERE u.vip_level > 0
                ORDER BY o.order_date DESC;
                """
            }
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                result = self.agent.run(
                    query=case["query"],
                    tools=self.tools_description
                )
                self.assertIn(case["expected"], result)

if __name__ == '__main__':
    unittest.main() 