"""Generate architecture diagrams for the Community Tool Lending Library.

Author: Vishvaksen Machana (25173421)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np


def draw_rounded_box(ax, x, y, w, h, text, color='#e3f2fd', edge='#1565c0',
                     fontsize=9, bold=False):
    """Draw a rounded rectangle with centered text."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                         facecolor=color, edgecolor=edge, linewidth=1.5)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, wrap=True)


def draw_arrow(ax, x1, y1, x2, y2, color='#555'):
    """Draw an arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))


def generate_architecture_diagram():
    """Generate the system architecture diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('Community Tool Lending Library - System Architecture',
                 fontsize=14, fontweight='bold', pad=20)

    # Frontend Layer
    draw_rounded_box(ax, 1, 8.5, 3, 1, 'React Frontend\n(Dashboard, Tools,\nUsers, Lendings, AWS)',
                     color='#fff3e0', edge='#e65100', fontsize=9, bold=True)

    # API Gateway
    draw_rounded_box(ax, 5.5, 8.5, 3, 1, 'API Gateway\n(REST Endpoints)',
                     color='#fce4ec', edge='#c62828', fontsize=9, bold=True)

    # Cognito
    draw_rounded_box(ax, 10, 8.5, 3, 1, 'Cognito\n(Authentication)',
                     color='#f3e5f5', edge='#7b1fa2', fontsize=9, bold=True)

    # Flask Backend
    draw_rounded_box(ax, 5.5, 6.5, 3, 1, 'Flask Backend\n(app.py + Routes)',
                     color='#e8f5e9', edge='#2e7d32', fontsize=10, bold=True)

    # Lambda Functions
    draw_rounded_box(ax, 0.5, 4.5, 2.5, 1, 'Lambda\n(Validation,\nNotifications)',
                     color='#fff8e1', edge='#f57f17', fontsize=8, bold=True)

    # Step Functions
    draw_rounded_box(ax, 3.5, 4.5, 2.5, 1, 'Step Functions\n(Lending Workflow\nOrchestration)',
                     color='#fce4ec', edge='#ad1457', fontsize=8, bold=True)

    # lendlib
    draw_rounded_box(ax, 6.5, 4.5, 2.5, 1, 'lendlib\n(Custom OOP Library)\nInventory, Lending,\nOverdue, History',
                     color='#e0f7fa', edge='#00838f', fontsize=7, bold=True)

    # CloudWatch
    draw_rounded_box(ax, 10, 4.5, 3, 1, 'CloudWatch\n(Monitoring, Logs,\nAlarms, Scheduling)',
                     color='#e8eaf6', edge='#283593', fontsize=8, bold=True)

    # DynamoDB
    draw_rounded_box(ax, 1, 2, 3, 1.2, 'DynamoDB\n(Tools Table)\n(Users Table)\n(Lendings Table)',
                     color='#e3f2fd', edge='#1565c0', fontsize=8, bold=True)

    # S3
    draw_rounded_box(ax, 5, 2, 2.5, 1.2, 'S3\n(Tool Images\nStorage)',
                     color='#e8f5e9', edge='#2e7d32', fontsize=8, bold=True)

    # SQLite
    draw_rounded_box(ax, 8.5, 2, 2.5, 1.2, 'SQLite\n(Local Dev\nDatabase)',
                     color='#f5f5f5', edge='#616161', fontsize=8, bold=True)

    # Arrows
    draw_arrow(ax, 4, 9, 5.5, 9)           # Frontend -> API Gateway
    draw_arrow(ax, 8.5, 9, 10, 9)          # API Gateway -> Cognito
    draw_arrow(ax, 7, 8.5, 7, 7.5)         # API Gateway -> Flask
    draw_arrow(ax, 5.5, 6.5, 1.75, 5.5)    # Flask -> Lambda
    draw_arrow(ax, 6.5, 6.5, 4.75, 5.5)    # Flask -> Step Functions
    draw_arrow(ax, 7.5, 6.5, 7.75, 5.5)    # Flask -> lendlib
    draw_arrow(ax, 8.5, 6.5, 11.5, 5.5)    # Flask -> CloudWatch
    draw_arrow(ax, 5.5, 6.5, 2.5, 3.2)     # Flask -> DynamoDB
    draw_arrow(ax, 7, 6.5, 6.25, 3.2)      # Flask -> S3
    draw_arrow(ax, 8, 6.5, 9.75, 3.2)      # Flask -> SQLite

    # Layer labels
    ax.text(0.2, 9.7, 'Presentation Layer', fontsize=10, fontstyle='italic', color='#888')
    ax.text(0.2, 7.2, 'Application Layer', fontsize=10, fontstyle='italic', color='#888')
    ax.text(0.2, 5.7, 'Service Layer', fontsize=10, fontstyle='italic', color='#888')
    ax.text(0.2, 3.5, 'Data Layer', fontsize=10, fontstyle='italic', color='#888')

    plt.tight_layout()
    plt.savefig('/Users/tarunchintakunta/Desktop/CPP/Vishvaksen/report/architecture_diagram.png',
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Architecture diagram saved.")


def generate_component_diagram():
    """Generate the component/class diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title('Community Tool Lending Library - Component Diagram',
                 fontsize=14, fontweight='bold', pad=20)

    # lendlib package components
    components = [
        (0.5, 7, 2.5, 1.2, 'Tool\n- name, category\n- condition\n- is_available', '#e3f2fd', '#1565c0'),
        (3.5, 7, 2.5, 1.2, 'User\n- username, email\n- role, trust_score\n- can_borrow()', '#e8f5e9', '#2e7d32'),
        (6.5, 7, 2.5, 1.2, 'LendingRecord\n- tool_id, borrower_id\n- status, due_date\n- approve(), activate()', '#fff3e0', '#e65100'),
        (0.5, 5, 2.5, 1.2, 'InventoryManager\n- add/get/update/\n  remove_tool()\n- search, filter', '#fce4ec', '#c62828'),
        (3.5, 5, 2.5, 1.2, 'LendingManager\n- create/approve/\n  activate/return\n- get_by_status()', '#f3e5f5', '#7b1fa2'),
        (6.5, 5, 2.5, 1.2, 'AvailabilityChecker\n- is_tool_available()\n- check_can_borrow()\n- get_summary()', '#e0f7fa', '#00838f'),
        (0.5, 3, 2.5, 1.2, 'OverdueDetector\n- scan_overdue()\n- calculate_penalty()\n- apply_penalties()', '#fff8e1', '#f57f17'),
        (3.5, 3, 2.5, 1.2, 'BorrowerHistory\n- get_return_rate()\n- reliability_score()\n- top_borrowers()', '#e8eaf6', '#283593'),
    ]

    for x, y, w, h, text, color, edge in components:
        draw_rounded_box(ax, x, y, w, h, text, color=color, edge=edge, fontsize=7, bold=False)

    # AWS Services column
    aws_services = [
        (10, 7.5, 3, 0.7, 'DynamoDBService', '#e3f2fd', '#1565c0'),
        (10, 6.5, 3, 0.7, 'S3Service', '#e8f5e9', '#2e7d32'),
        (10, 5.5, 3, 0.7, 'LambdaService', '#fff3e0', '#e65100'),
        (10, 4.5, 3, 0.7, 'CognitoService', '#f3e5f5', '#7b1fa2'),
        (10, 3.5, 3, 0.7, 'StepFunctionsService', '#fce4ec', '#c62828'),
        (10, 2.5, 3, 0.7, 'CloudWatchService', '#e8eaf6', '#283593'),
        (10, 1.5, 3, 0.7, 'APIGatewayService', '#e0f7fa', '#00838f'),
    ]

    for x, y, w, h, text, color, edge in aws_services:
        draw_rounded_box(ax, x, y, w, h, text, color=color, edge=edge, fontsize=8, bold=True)

    # Labels
    ax.text(0.5, 8.5, 'lendlib - Custom OOP Library', fontsize=12, fontweight='bold', color='#333')
    ax.text(10, 8.5, 'AWS Service Wrappers', fontsize=12, fontweight='bold', color='#333')

    # Flask routes
    draw_rounded_box(ax, 5.5, 1, 3.5, 1.2, 'Flask Routes\n/api/tools | /api/users\n/api/lendings | /api/aws',
                     color='#f5f5f5', edge='#616161', fontsize=8, bold=True)
    ax.text(5.5, 2.4, 'Backend API Layer', fontsize=10, fontweight='bold', color='#333')

    # Connecting arrows
    draw_arrow(ax, 1.75, 5, 1.75, 4.2)   # InventoryManager -> OverdueDetector
    draw_arrow(ax, 4.75, 5, 4.75, 4.2)   # LendingManager -> BorrowerHistory
    draw_arrow(ax, 7.75, 5, 7.75, 4.2)   # AvailabilityChecker down
    draw_arrow(ax, 9, 5.6, 10, 5.6)       # to AWS services
    draw_arrow(ax, 9, 7.5, 10, 7.5)       # to AWS services

    plt.tight_layout()
    plt.savefig('/Users/tarunchintakunta/Desktop/CPP/Vishvaksen/report/component_diagram.png',
                dpi=150, bbox_inches='tight')
    plt.close()
    print("Component diagram saved.")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_component_diagram()
    print("All diagrams generated successfully.")
