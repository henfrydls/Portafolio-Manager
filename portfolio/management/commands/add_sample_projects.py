from django.core.management.base import BaseCommand
from portfolio.models import Project, Technology
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = 'Add sample projects for testing pagination'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=12,
            help='Number of sample projects to create (default: 12)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample project data
        sample_projects = [
            {
                'title': 'E-Commerce Platform',
                'description': '🛒 Full-stack e-commerce solution with React frontend, Django REST API, and PostgreSQL database. Features include user authentication, product catalog, shopping cart, payment integration with Stripe, order management, and admin dashboard.',
                'project_type': 'website',
                'github_url': 'https://github.com/example/ecommerce-platform',
                'project_url': 'https://ecommerce-demo.example.com',
                'technologies': ['Python', 'Django', 'React', 'PostgreSQL', 'Redis'],
                'featured': True,
                'emoji': '🛒'
            },
            {
                'title': 'Task Management API',
                'description': '📋 RESTful API for task management with JWT authentication, role-based permissions, real-time notifications via WebSockets, and comprehensive documentation with Swagger/OpenAPI.',
                'project_type': 'api',
                'github_url': 'https://github.com/example/task-api',
                'technologies': ['Python', 'FastAPI', 'MongoDB', 'Docker'],
                'featured': False,
                'emoji': '📋'
            },
            {
                'title': 'Data Visualization Dashboard',
                'description': '📊 Interactive dashboard built with D3.js and Vue.js for visualizing complex datasets. Features real-time data updates, multiple chart types, filtering capabilities, and export functionality.',
                'project_type': 'website',
                'github_url': 'https://github.com/example/data-dashboard',
                'project_url': 'https://dashboard-demo.example.com',
                'technologies': ['JavaScript', 'Vue.js', 'D3.js', 'Node.js'],
                'featured': True,
                'emoji': '📊'
            },
            {
                'title': 'Mobile Fitness Tracker',
                'description': '💪 React Native mobile app for fitness tracking with workout logging, progress visualization, social features, and integration with wearable devices.',
                'project_type': 'mobile_app',
                'github_url': 'https://github.com/example/fitness-tracker',
                'technologies': ['React Native', 'TypeScript', 'Firebase', 'Redux'],
                'featured': False,
                'emoji': '💪'
            },
            {
                'title': 'Machine Learning Pipeline',
                'description': '🤖 End-to-end ML pipeline for predictive analytics using Python, scikit-learn, and Apache Airflow. Includes data preprocessing, model training, evaluation, and deployment with Docker.',
                'project_type': 'tool',
                'github_url': 'https://github.com/example/ml-pipeline',
                'technologies': ['Python', 'scikit-learn', 'Apache Airflow', 'Docker'],
                'featured': True,
                'emoji': '🤖'
            },
            {
                'title': 'Real-time Chat Application',
                'description': '💬 WebSocket-based chat application with multiple rooms, file sharing, emoji reactions, and message history. Built with Socket.io and Express.js.',
                'project_type': 'website',
                'github_url': 'https://github.com/example/chat-app',
                'project_url': 'https://chat-demo.example.com',
                'technologies': ['Node.js', 'Socket.io', 'Express.js', 'MongoDB'],
                'featured': False,
                'emoji': '💬'
            },
            {
                'title': 'Blockchain Voting System',
                'description': '🗳️ Decentralized voting system built on Ethereum blockchain with smart contracts, ensuring transparency and immutability of votes. Features voter registration and result verification.',
                'project_type': 'other',
                'github_url': 'https://github.com/example/blockchain-voting',
                'technologies': ['Solidity', 'Web3.js', 'Ethereum', 'React'],
                'featured': True,
                'emoji': '🗳️'
            },
            {
                'title': 'DevOps Automation Tools',
                'description': '⚙️ Collection of automation scripts and tools for CI/CD pipelines, infrastructure as code with Terraform, monitoring with Prometheus, and deployment automation.',
                'project_type': 'tool',
                'github_url': 'https://github.com/example/devops-tools',
                'technologies': ['Python', 'Terraform', 'Docker', 'Kubernetes'],
                'featured': False,
                'emoji': '⚙️'
            },
            {
                'title': 'Content Management System',
                'description': '📝 Headless CMS built with Node.js and GraphQL, featuring flexible content modeling, multi-language support, role-based access control, and RESTful API.',
                'project_type': 'website',
                'github_url': 'https://github.com/example/headless-cms',
                'project_url': 'https://cms-demo.example.com',
                'technologies': ['Node.js', 'GraphQL', 'MongoDB', 'Express.js'],
                'featured': True,
                'emoji': '📝'
            },
            {
                'title': 'IoT Sensor Network',
                'description': '🌡️ IoT system for environmental monitoring with Raspberry Pi sensors, MQTT messaging, real-time data processing, and web-based monitoring dashboard.',
                'project_type': 'other',
                'github_url': 'https://github.com/example/iot-sensors',
                'technologies': ['Python', 'Raspberry Pi', 'MQTT', 'InfluxDB'],
                'featured': False,
                'emoji': '🌡️'
            },
            {
                'title': 'Microservices Architecture',
                'description': '🏗️ Scalable microservices architecture with API Gateway, service discovery, distributed tracing, and containerized deployment using Docker and Kubernetes.',
                'project_type': 'framework',
                'github_url': 'https://github.com/example/microservices',
                'technologies': ['Java', 'Spring Boot', 'Docker', 'Kubernetes'],
                'featured': True,
                'emoji': '🏗️'
            },
            {
                'title': 'Game Development Engine',
                'description': '🎮 2D game engine built with C++ and OpenGL, featuring physics simulation, sprite animation, audio system, and cross-platform compatibility.',
                'project_type': 'library',
                'github_url': 'https://github.com/example/game-engine',
                'technologies': ['C++', 'OpenGL', 'SDL2', 'CMake'],
                'featured': False,
                'emoji': '🎮'
            }
        ]

        # Get or create technologies
        tech_objects = {}
        for project_data in sample_projects[:count]:
            for tech_name in project_data['technologies']:
                if tech_name not in tech_objects:
                    tech_obj, created = Technology.objects.get_or_create(
                        name=tech_name,
                        defaults={
                            'color': self.get_tech_color(tech_name),
                            'icon': self.get_tech_icon(tech_name)
                        }
                    )
                    tech_objects[tech_name] = tech_obj
                    if created:
                        self.stdout.write(f'Created technology: {tech_name}')

        # Create projects
        created_count = 0
        for i, project_data in enumerate(sample_projects[:count]):
            # Check if project already exists
            if Project.objects.filter(title=project_data['title']).exists():
                self.stdout.write(f'Project "{project_data["title"]}" already exists, skipping...')
                continue

            # Create project
            project = Project.objects.create(
                title=project_data['title'],
                slug=slugify(project_data['title']),
                description=project_data['description'],
                detailed_description=project_data['description'],
                project_type=project_data.get('project_type', 'other'),
                github_url=project_data['github_url'],
                demo_url=project_data.get('project_url', ''),
                featured=project_data['featured'],
                visibility='public',
                order=i + 1,
                emoji=project_data.get('emoji', ''),
                stars_count=random.randint(5, 150),
                forks_count=random.randint(1, 25)
            )

            # Add technologies
            for tech_name in project_data['technologies']:
                project.technologies.add(tech_objects[tech_name])

            created_count += 1
            self.stdout.write(f'Created project: {project.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample projects!')
        )

    def get_tech_color(self, tech_name):
        """Get appropriate color for technology"""
        colors = {
            'Python': '#3776ab',
            'Django': '#092e20',
            'React': '#61dafb',
            'JavaScript': '#f7df1e',
            'TypeScript': '#3178c6',
            'Node.js': '#339933',
            'Vue.js': '#4fc08d',
            'PostgreSQL': '#336791',
            'MongoDB': '#47a248',
            'Redis': '#dc382d',
            'Docker': '#2496ed',
            'Kubernetes': '#326ce5',
            'FastAPI': '#009688',
            'Express.js': '#000000',
            'Socket.io': '#010101',
            'GraphQL': '#e10098',
            'Solidity': '#363636',
            'Web3.js': '#f16822',
            'Ethereum': '#627eea',
            'Terraform': '#623ce4',
            'Java': '#ed8b00',
            'Spring Boot': '#6db33f',
            'C++': '#00599c',
            'OpenGL': '#5586a4',
            'Firebase': '#ffca28',
            'Redux': '#764abc',
            'D3.js': '#f68e56',
            'Apache Airflow': '#017cee',
            'scikit-learn': '#f7931e',
            'Raspberry Pi': '#c51a4a',
            'MQTT': '#660066',
            'InfluxDB': '#22adf6',
            'SDL2': '#1e90ff',
            'CMake': '#064f8c'
        }
        return colors.get(tech_name, '#666666')

    def get_tech_icon(self, tech_name):
        """Get appropriate icon for technology"""
        icons = {
            'Python': 'fab fa-python',
            'Django': 'fas fa-server',
            'React': 'fab fa-react',
            'JavaScript': 'fab fa-js-square',
            'TypeScript': 'fab fa-js-square',
            'Node.js': 'fab fa-node-js',
            'Vue.js': 'fab fa-vuejs',
            'PostgreSQL': 'fas fa-database',
            'MongoDB': 'fas fa-database',
            'Redis': 'fas fa-database',
            'Docker': 'fab fa-docker',
            'Kubernetes': 'fas fa-dharmachakra',
            'FastAPI': 'fas fa-rocket',
            'Express.js': 'fas fa-server',
            'Socket.io': 'fas fa-plug',
            'GraphQL': 'fas fa-project-diagram',
            'Solidity': 'fas fa-code',
            'Web3.js': 'fab fa-ethereum',
            'Ethereum': 'fab fa-ethereum',
            'Terraform': 'fas fa-cloud',
            'Java': 'fab fa-java',
            'Spring Boot': 'fas fa-leaf',
            'C++': 'fas fa-code',
            'OpenGL': 'fas fa-cube',
            'Firebase': 'fas fa-fire',
            'Redux': 'fas fa-store',
            'D3.js': 'fas fa-chart-bar',
            'Apache Airflow': 'fas fa-wind',
            'scikit-learn': 'fas fa-brain',
            'Raspberry Pi': 'fas fa-microchip',
            'MQTT': 'fas fa-broadcast-tower',
            'InfluxDB': 'fas fa-database',
            'SDL2': 'fas fa-gamepad',
            'CMake': 'fas fa-tools'
        }
        return icons.get(tech_name, 'fas fa-code')