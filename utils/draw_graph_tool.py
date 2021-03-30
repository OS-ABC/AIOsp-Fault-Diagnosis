import networkx as nx
import matplotlib.pyplot as plt
try:
    import pygraphviz
    from networkx.drawing.nx_agraph import graphviz_layout
except ImportError:
    try:
        import pydot
        from networkx.drawing.nx_pydot import graphviz_layout
    except ImportError:
        raise ImportError("This example needs Graphviz and either "
                              "PyGraphviz or PyDotPlus")
if __name__ == '__main__':
    dg = nx.DiGraph()
    # dg.add_nodes_from(["0", "1", "2", "3", "4"])
    nodes = ["os_022:osb_001", "docker_001:csf_001","docker_008:csf_005","docker_007:csf_004","docker_008:csf_003","docker_008:csf_002","db_003","db_007","db_009","docker_001:fly_remote_001","os_021:osb_001","docker_003:csf_001", "docker_005:csf_005","docker_006:csf_004","docker_005:csf_003","docker_006:csf_002","docker_003:fly_remote_001","docker_006:csf_003", "docker_005:csf_002","docker_004:csf_001","docker_006:csf_005","docker_004:fly_remote_001","docker_007:csf_005","docker_007:csf_003","docker_008:csf_004","docker_007:csf_002","docker_005:csf_004","docker_002:csf_001","docker_002:fly_remote_001"]
    edges = [("os_022:osb_001","docker_001:csf_001"),("docker_001:csf_001","docker_008:csf_005"), ("docker_001:csf_001","docker_007:csf_004"), ("docker_001:csf_001","docker_008:csf_003"), ("docker_001:csf_001","docker_008:csf_002"), ("docker_008:csf_005", "db_003"), ("docker_007:csf_004", "db_003"), ("docker_008:csf_003", "db_003"), ("docker_008:csf_002", "db_003"), ("docker_001:csf_001", "db_007"), ("docker_001:csf_001", "db_009"), ("docker_001:csf_001", "docker_001:fly_remote_001"),("os_021:osb_001", "docker_003:csf_001"), ("docker_003:csf_001","docker_005:csf_005"), ("docker_003:csf_001", "docker_006:csf_004"), ("docker_003:csf_001","docker_005:csf_003"), ("docker_003:csf_001", "docker_006:csf_002"), ("docker_005:csf_005","db_003"), ("docker_006:csf_004","db_003"), ("docker_005:csf_003", "db_003"), ("docker_006:csf_002", "db_003"), ("docker_003:csf_001", "db_007"), ("docker_003:csf_001", "db_009"), ("docker_003:csf_001","docker_003:fly_remote_001"), ("docker_003:csf_001","docker_006:csf_003"),("docker_003:csf_001","docker_005:csf_002"), ("docker_006:csf_003", "db_003"),("docker_005:csf_002","db_003"), ("os_021:osb_001","docker_004:csf_001"), ("docker_004:csf_001","docker_006:csf_005"), ("docker_004:csf_001","docker_006:csf_004"), ("docker_004:csf_001", "docker_006:csf_003"),("docker_004:csf_001","docker_006:csf_002"), ("docker_006:csf_005", "db_003"),("docker_004:csf_001","db_007"),("docker_004:csf_001","db_009"), ("docker_004:csf_001", "docker_004:fly_remote_001"), ("docker_001:csf_001","docker_007:csf_005"), ("docker_001:csf_001", "docker_007:csf_003"), ("docker_007:csf_005", "db_003"),("docker_007:csf_003","db_003"), ("docker_001:csf_001","docker_008:csf_004"), ("docker_001:csf_001", "docker_007:csf_002"),("docker_008:csf_004", "db_003"), ("docker_007:csf_002", "db_003"), ("docker_003:csf_001","docker_005:csf_004"), ("docker_005:csf_004", "db_003"), ("docker_004:csf_001","docker_005:csf_005"), ("os_022:osb_001","docker_002:csf_001"), ("docker_002:csf_001","docker_007:csf_005"), ("docker_002:csf_001","docker_007:csf_004"),("docker_002:csf_001","docker_007:csf_003"), ("docker_002:csf_001", "docker_007:csf_002"), ("docker_002:csf_001","db_007"), ("docker_002:csf_001","db_009"), ("docker_002:csf_001","docker_002:fly_remote_001"), ("docker_004:csf_001", "docker_005:csf_004"), ("docker_004:csf_001","docker_005:csf_002"), ("docker_003:csf_001", "docker_006:csf_005"), ("docker_004:csf_001", "docker_005:csf_003"), ("docker_002:csf_001", "docker_008:csf_005"), ("docker_002:csf_001", "docker_008:csf_002"), ("docker_002:csf_001","docker_008:csf_004"), ("docker_002:csf_001","docker_008:csf_003")]
    dg.add_nodes_from(nodes)
    dg.add_edges_from(edges)
    # dg.add_weighted_edges_from(list)
    # pos = nx.graphviz_layout(dg, prog='dot')

    nx.draw(dg,
            pos=nx.graphviz_layout(dg, prog='dot'),  # pos 指的是布局,主要有spring_layout,random_layout,circle_layout,shell_layout
            node_color='g',  # node_color指节点颜色,有rbykw,同理edge_color
            edge_color='r',
            with_labels=True,  # with_labels指节点是否显示名字
            font_size=18,  # font_size表示字体大小,font_color表示字的颜色
            node_size=60)  # font_size表示字体大小,font_color表示字的颜色
    plt.show()
    pass