import pytest
from loguru import logger
from rag_service.app.core.agents.text2sql import create_sql_agent
from rag_service.app.core.utils.timer import timer

# 配置日志
logger.remove()
logger.add(
    "logs/test_text2sql_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# 基础查询测试用例
basic_queries = [
    pytest.param(
        "简单SELECT查询",
        "查询所有用户的姓名和邮箱",
        "SELECT name, email FROM users;",
        id="simple_select"
    ),
    pytest.param(
        "带WHERE条件的查询",
        "查找年龄大于25岁的用户",
        "SELECT * FROM users WHERE age > 25;",
        id="where_condition"
    ),
    pytest.param(
        "多表JOIN查询",
        "查询所有用户的订单信息，包括用户名和订单金额",
        "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id;",
        id="join_query"
    )
]

# 嵌套查询测试用例
nested_queries = [
    pytest.param(
        "子查询在WHERE子句中",
        """
        假设有两个表：
        ```sql
        create table students (id int, name string, class_id int);
        create table classes (id int, name string, teacher_id int);
        create table teachers (id int, name string);
        ```
        查找所有由'张老师'教的学生的姓名
        """,
        """
        SELECT s.name 
        FROM students s 
        WHERE s.class_id IN (
            SELECT c.id 
            FROM classes c 
            JOIN teachers t ON c.teacher_id = t.id 
            WHERE t.name = '张老师'
        );
        """,
        id="where_subquery"
    ),
    pytest.param(
        "子查询在FROM子句中",
        """
        假设有两个表：
        ```sql
        create table orders (id int, user_id int, amount decimal, order_date date);
        create table users (id int, name string);
        ```
        查询每个用户的平均订单金额，并找出高于平均值的用户
        """,
        """
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
        """,
        id="from_subquery"
    )
]

# UNION查询测试用例
union_queries = [
    pytest.param(
        "简单UNION查询",
        """
        假设有两个表：
        ```sql
        create table active_users (id int, name string, last_login date);
        create table inactive_users (id int, name string, last_login date);
        ```
        查询所有用户（包括活跃和非活跃）的姓名和最后登录时间
        """,
        """
        SELECT name, last_login
        FROM active_users
        UNION
        SELECT name, last_login
        FROM inactive_users;
        """,
        id="simple_union"
    ),
    pytest.param(
        "UNION ALL查询",
        """
        假设有两个表：
        ```sql
        create table current_employees (id int, name string, salary decimal);
        create table former_employees (id int, name string, salary decimal);
        ```
        查询所有员工（包括现任和前任）的姓名和薪资，保留重复记录
        """,
        """
        SELECT name, salary
        FROM current_employees
        UNION ALL
        SELECT name, salary
        FROM former_employees;
        """,
        id="union_all"
    )
]

# 复杂查询测试用例
complex_queries = [
    pytest.param(
        "复杂嵌套查询",
        """
        假设有三个表：
        ```sql
        create table students (id int, name string, class_id int);
        create table classes (id int, name string, teacher_id int);
        create table scores (student_id int, subject string, score decimal);
        ```
        查询每个班级中，成绩高于该班级平均分的学生姓名和成绩
        """,
        """
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
        """,
        id="complex_nested"
    ),
    pytest.param(
        "UNION和子查询组合",
        """
        假设有三个表：
        ```sql
        create table current_orders (id int, user_id int, amount decimal, order_date date);
        create table historical_orders (id int, user_id int, amount decimal, order_date date);
        create table users (id int, name string, vip_level int);
        ```
        查询所有VIP用户（vip_level > 0）的订单信息，包括当前和历史订单
        """,
        """
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
        """,
        id="union_subquery"
    )
]

@pytest.fixture(scope="module")
def sql_agent():
    """创建SQL Agent的fixture"""
    logger.info("初始化 SQL Agent...")
    agent = create_sql_agent()
    tools_description = "\n".join([
        f"{tool.name}: {tool.description}"
        for tool in agent.tools
    ])
    logger.info("SQL Agent 初始化完成")
    return agent, tools_description

@timer
@pytest.mark.parametrize("name,query,expected", basic_queries)
def test_basic_queries(sql_agent, name, query, expected):
    """测试基本的SQL查询场景"""
    agent, tools_description = sql_agent
    logger.info(f"开始测试: {name}")
    logger.debug(f"输入查询: {query}")
    
    result = agent.run(
        query=query,
        tools=tools_description
    )
    
    logger.debug(f"生成SQL: {result}")
    logger.debug(f"期望SQL: {expected}")
    assert expected in result
    logger.info(f"测试完成: {name}")

@timer
@pytest.mark.parametrize("name,query,expected", nested_queries)
def test_nested_queries(sql_agent, name, query, expected):
    """测试嵌套查询场景"""
    agent, tools_description = sql_agent
    logger.info(f"开始测试: {name}")
    logger.debug(f"输入查询: {query}")
    
    result = agent.run(
        query=query,
        tools=tools_description
    )
    
    logger.debug(f"生成SQL: {result}")
    logger.debug(f"期望SQL: {expected}")
    assert expected in result
    logger.info(f"测试完成: {name}")

@timer
@pytest.mark.parametrize("name,query,expected", union_queries)
def test_union_queries(sql_agent, name, query, expected):
    """测试UNION查询场景"""
    agent, tools_description = sql_agent
    logger.info(f"开始测试: {name}")
    logger.debug(f"输入查询: {query}")
    
    result = agent.run(
        query=query,
        tools=tools_description
    )
    
    logger.debug(f"生成SQL: {result}")
    logger.debug(f"期望SQL: {expected}")
    assert expected in result
    logger.info(f"测试完成: {name}")

@timer
@pytest.mark.parametrize("name,query,expected", complex_queries)
def test_complex_queries(sql_agent, name, query, expected):
    """测试复杂查询场景"""
    agent, tools_description = sql_agent
    logger.info(f"开始测试: {name}")
    logger.debug(f"输入查询: {query}")
    
    result = agent.run(
        query=query,
        tools=tools_description
    )
    
    logger.debug(f"生成SQL: {result}")
    logger.debug(f"期望SQL: {expected}")
    assert expected in result
    logger.info(f"测试完成: {name}") 