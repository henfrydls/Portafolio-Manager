from django.core.management.base import BaseCommand
from portfolio.models import Technology


class Command(BaseCommand):
    help = 'Pobla la base de datos con tecnologías comunes predefinidas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Actualizar tecnologías existentes con iconos y colores sugeridos',
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Poblar solo una categoría específica (languages, frontend, backend, databases, devops, tools, mobile)',
        )

    def handle(self, *args, **options):
        # Definir tecnologías por categorías
        technologies_data = {
            'languages': [
                ('Python', 'fab fa-python', '#3776ab'),
                ('JavaScript', 'fab fa-js-square', '#f7df1e'),
                ('TypeScript', 'fab fa-js-square', '#3178c6'),
                ('Java', 'fab fa-java', '#ed8b00'),
                ('PHP', 'fab fa-php', '#777bb4'),
                ('Swift', 'fab fa-swift', '#fa7343'),
                ('Rust', 'fab fa-rust', '#000000'),
                ('Go', 'fab fa-golang', '#00add8'),
                ('C++', 'fas fa-code', '#00599c'),
                ('C#', 'fas fa-code', '#239120'),
                ('Ruby', 'fas fa-gem', '#cc342d'),
                ('Kotlin', 'fab fa-android', '#7f52ff'),
            ],
            'frontend': [
                ('React', 'fab fa-react', '#61dafb'),
                ('Vue.js', 'fab fa-vuejs', '#4fc08d'),
                ('Angular', 'fab fa-angular', '#dd0031'),
                ('HTML', 'fab fa-html5', '#e34f26'),
                ('CSS', 'fab fa-css3-alt', '#1572b6'),
                ('Sass', 'fab fa-sass', '#cc6699'),
                ('Bootstrap', 'fab fa-bootstrap', '#7952b3'),
                ('Tailwind CSS', 'fas fa-wind', '#06b6d4'),
            ],
            'backend': [
                ('Django', 'fas fa-server', '#092e20'),
                ('Flask', 'fas fa-flask', '#000000'),
                ('Node.js', 'fab fa-node-js', '#339933'),
                ('Express.js', 'fas fa-server', '#000000'),
                ('Laravel', 'fab fa-laravel', '#ff2d20'),
                ('Spring Boot', 'fas fa-leaf', '#6db33f'),
                ('FastAPI', 'fas fa-rocket', '#009688'),
            ],
            'databases': [
                ('PostgreSQL', 'fas fa-database', '#336791'),
                ('MySQL', 'fas fa-database', '#4479a1'),
                ('MongoDB', 'fas fa-database', '#47a248'),
                ('Redis', 'fas fa-database', '#dc382d'),
                ('SQLite', 'fas fa-database', '#003b57'),
            ],
            'devops': [
                ('Docker', 'fab fa-docker', '#2496ed'),
                ('Kubernetes', 'fas fa-dharmachakra', '#326ce5'),
                ('AWS', 'fab fa-aws', '#ff9900'),
                ('Google Cloud', 'fab fa-google', '#4285f4'),
                ('Azure', 'fab fa-microsoft', '#0078d4'),
                ('Git', 'fab fa-git-alt', '#f05032'),
                ('GitHub', 'fab fa-github', '#181717'),
                ('GitLab', 'fab fa-gitlab', '#fc6d26'),
            ],
            'tools': [
                ('Linux', 'fab fa-linux', '#fcc624'),
                ('Ubuntu', 'fab fa-ubuntu', '#e95420'),
                ('Windows', 'fab fa-windows', '#0078d6'),
                ('macOS', 'fab fa-apple', '#000000'),
                ('VS Code', 'fas fa-code', '#007acc'),
                ('Figma', 'fab fa-figma', '#f24e1e'),
                ('Slack', 'fab fa-slack', '#4a154b'),
                ('Trello', 'fab fa-trello', '#0079bf'),
            ],
            'mobile': [
                ('Android', 'fab fa-android', '#3ddc84'),
                ('iOS', 'fab fa-apple', '#000000'),
                ('React Native', 'fab fa-react', '#61dafb'),
                ('Flutter', 'fas fa-mobile-alt', '#02569b'),
            ],
            'other': [
                ('WordPress', 'fab fa-wordpress', '#21759b'),
                ('Shopify', 'fab fa-shopify', '#7ab55c'),
                ('Firebase', 'fas fa-fire', '#ffca28'),
                ('GraphQL', 'fas fa-project-diagram', '#e10098'),
                ('REST API', 'fas fa-exchange-alt', '#009688'),
            ]
        }

        # Filtrar por categoría si se especifica
        if options['category']:
            if options['category'] not in technologies_data:
                self.stdout.write(
                    self.style.ERROR(f'Categoría "{options["category"]}" no válida. '
                                   f'Opciones: {", ".join(technologies_data.keys())}')
                )
                return
            technologies_data = {options['category']: technologies_data[options['category']]}

        created_count = 0
        updated_count = 0
        
        for category, techs in technologies_data.items():
            self.stdout.write(f'\nProcesando categoría: {category.upper()}')
            
            for name, icon, color in techs:
                tech, created = Technology.objects.get_or_create(
                    name=name,
                    defaults={'icon': icon, 'color': color}
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Creada: {name}')
                    )
                elif options['update']:
                    # Actualizar si los valores son diferentes
                    updated = False
                    if tech.icon != icon:
                        tech.icon = icon
                        updated = True
                    if tech.color != color:
                        tech.color = color
                        updated = True
                    
                    if updated:
                        tech.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'  ↻ Actualizada: {name}')
                        )
                    else:
                        self.stdout.write(
                            self.style.HTTP_INFO(f'  - Sin cambios: {name}')
                        )
                else:
                    self.stdout.write(
                        self.style.HTTP_INFO(f'  - Ya existe: {name}')
                    )

        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Tecnologías creadas: {created_count}'))
        if options['update']:
            self.stdout.write(self.style.WARNING(f'Tecnologías actualizadas: {updated_count}'))
        
        total_techs = Technology.objects.count()
        self.stdout.write(self.style.HTTP_INFO(f'Total de tecnologías en la base de datos: {total_techs}'))
        
        if not options['update'] and Technology.objects.filter(icon='', color='#000000').exists():
            self.stdout.write('\n' + self.style.HTTP_NOT_MODIFIED(
                'Consejo: Usa --update para actualizar tecnologías existentes con iconos y colores sugeridos'
            ))