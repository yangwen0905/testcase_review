import json
from typing import List, Dict
from xmindparser import xmind_to_dict
import os
import json
import yaml

"""将XMind文件转换为json格式"""


def transform_type_to_json(file_path):
    # 转换XMind为Python字典
    data = xmind_to_dict(file_path)

    # 转换为JSON（解决中文乱码问题）
    json_filename = os.path.splitext(file_path)[0] + ".json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"文件转换为json格式成功")
    return json_filename


"""将XMind文件转换为yaml格式"""


def transform_type_to_yaml(file_path):
    # 转换XMind为Python字典
    data = xmind_to_dict(file_path)

    # 转换为YAML
    yaml_filename = os.path.splitext(file_path)[0] + ".yml"
    with open(yaml_filename, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"文件转换yaml格式成功")
    return yaml_filename


"""根据json文件生成测试用例"""


def build_test_case(scenario: str, prerequisite: str, steps: List[str], expected: List[str]) -> Dict:
    return {
        "test_case_name": scenario,
        "description": f"验证 {scenario} 功能",
        "prerequisites": [{"description": prerequisite}] if prerequisite else [],
        "steps": [{"description": s} for s in steps],
        "expected_results": [{"result": e} for e in expected]
    }


def traverse_scenarios(nodes: List, results: List) -> None:
    for scenario_node in nodes:
        scenario_title = scenario_node.get("title", "").strip()
        children = scenario_node.get("topics", [])
        if not children:
            continue

        # 检查第一个子节点，判断场景类型
        first_child = children[0]
        # 判断情况1：有前提条件（即第一个子节点有子节点，并且这些子节点中至少有一个有子节点）
        has_grandchildren = False
        if first_child.get("topics"):
            for child in first_child.get("topics", []):
                if child.get("topics"):
                    has_grandchildren = True
                    break

        if has_grandchildren:
            # 情况1：有前提条件
            for prereq_node in children:
                prerequisite = prereq_node.get("title", "").strip()
                steps = []
                expected = []
                # 遍历前提条件节点的子节点（步骤节点）
                for step_node in prereq_node.get("topics", []):
                    step_title = step_node.get("title", "").strip()
                    steps.append(step_title)
                    # 取步骤节点的第一个子节点（预期结果）
                    if step_node.get("topics") and step_node["topics"]:
                        # 取第一个子节点的标题
                        exp_title = step_node["topics"][0].get("title", "").strip()
                        expected.append(exp_title)
                    else:
                        expected.append("")
                # 构建测试用例
                case = build_test_case(scenario_title, prerequisite, steps, expected)
                if case:
                    results.append(case)
        else:
            # 情况2：无前提条件
            prerequisite = ""
            steps = []
            expected = []
            for step_node in children:
                step_title = step_node.get("title", "").strip()
                steps.append(step_title)
                if step_node.get("topics") and step_node["topics"]:
                    exp_title = step_node["topics"][0].get("title", "").strip()
                    expected.append(exp_title)
                else:
                    expected.append("")
            case = build_test_case(scenario_title, prerequisite, steps, expected)
            if case:
                results.append(case)


def convert(input_file: str, output_file: str) -> None:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 获取根节点（跳过workbook层）
    root = data[0]["topic"]["topics"]
    test_cases = []

    # 遍历所有场景节点
    traverse_scenarios(root, test_cases)

    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)
