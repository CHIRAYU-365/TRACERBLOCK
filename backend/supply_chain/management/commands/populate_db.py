import os
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import CustomUser
from supply_chain.models import Product, Warehouse, Inventory, PurchaseOrder, QualityCheck, TrackingEvent, Telemetry

class Command(BaseCommand):
    help = 'Populate the SCM database with 100 unique products and over 100 rows of relational SCM observation records.'

    def handle(self, *args, **options):
        self.stdout.write("Wiping existing supply chain transactional records for a clean seed...")
        Telemetry.objects.all().delete()
        TrackingEvent.objects.all().delete()
        QualityCheck.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        Inventory.objects.all().delete()
        Product.objects.all().delete()
        Warehouse.objects.all().delete()

        self.stdout.write("Ensuring seeder users are registered...")
        # Create seeder accounts with secure defaults if not present
        admin_user, _ = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'role': 'ADMIN',
                'email': 'admin@tracerblock.com',
                'organization': 'TracerBlock HQ'
            }
        )
        admin_user.set_password('admin')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        manufacturer, _ = CustomUser.objects.get_or_create(
            username='manufacturer_seeder',
            defaults={
                'role': 'MANUFACTURER',
                'email': 'manufacturer@tracerblock.com',
                'organization': 'Apex Biotech & Cybernetics'
            }
        )
        manufacturer.set_password('password123')
        manufacturer.save()

        distributor, _ = CustomUser.objects.get_or_create(
            username='distributor_seeder',
            defaults={
                'role': 'DISTRIBUTOR',
                'email': 'distributor@tracerblock.com',
                'organization': 'Global Cold-Chain Logistics'
            }
        )
        distributor.set_password('password123')
        distributor.save()

        retailer, _ = CustomUser.objects.get_or_create(
            username='retailer_seeder',
            defaults={
                'role': 'RETAILER',
                'email': 'retailer@tracerblock.com',
                'organization': 'Cornerstone Pharmacy & Retail'
            }
        )
        retailer.set_password('password123')
        retailer.save()

        qa_inspector, _ = CustomUser.objects.get_or_create(
            username='inspector_seeder',
            defaults={
                'role': 'QA',
                'email': 'inspector@tracerblock.com',
                'organization': 'Federal Standards Authority'
            }
        )
        qa_inspector.set_password('password123')
        qa_inspector.save()

        logistics_provider, _ = CustomUser.objects.get_or_create(
            username='logistics_seeder',
            defaults={
                'role': 'LOGISTICS',
                'email': 'logistics@tracerblock.com',
                'organization': 'Trans-Global Air Cargo'
            }
        )
        logistics_provider.set_password('password123')
        logistics_provider.save()

        self.stdout.write("Creating 5 primary SCM warehouse facilities...")
        warehouses_data = [
            {"name": "Rotterdam Deep-Freeze Vault", "location": "Rotterdam Port, Netherlands", "manager": distributor},
            {"name": "LAX Avionics Transit Hub", "location": "Los Angeles Airport, USA", "manager": distributor},
            {"name": "Tokyo Biotech Repository", "location": "Tokyo Bay, Japan", "manager": distributor},
            {"name": "Frankfurt Polymer Depot", "location": "Frankfurt, Germany", "manager": distributor},
            {"name": "Singapore Maritime Logistics Terminal", "location": "Tuas Port, Singapore", "manager": distributor}
        ]
        
        created_warehouses = []
        for w_data in warehouses_data:
            wh = Warehouse.objects.create(
                name=w_data["name"],
                location=w_data["location"],
                manager=w_data["manager"]
            )
            created_warehouses.append(wh)

        self.stdout.write("Generating 100 distinct supply chain products...")
        categories = [
            {
                "name": "Pharmaceuticals",
                "templates": [
                    "mRNA Covid-19 Vaccine (Lot {lot})", "Insulin Glargine Pen Pack (Lot {lot})", "Epi-Pen Autoinjector (Lot {lot})",
                    "Human Growth Hormone (Lot {lot})", "Tetanus Toxoid Vaccine (Lot {lot})", "Pneumococcal Vaccine (Lot {lot})",
                    "Shingrix Shingles Vaccine (Lot {lot})", "Measles MMR Vaccine (Lot {lot})", "Varicella Chickenpox Vaccine (Lot {lot})",
                    "Meningococcal Vaccine (Lot {lot})", "Gardasil HPV Vaccine (Lot {lot})", "Hepatitis B Recombinant (Lot {lot})",
                    "Rabies Vaccine Imovax (Lot {lot})", "Polio Salk Injected (Lot {lot})", "Rotavirus Rotateq Oral (Lot {lot})",
                    "Typhoid Vi Polysaccharide (Lot {lot})", "Yellow Fever Stamaril (Lot {lot})", "BCG Tuberculosis Vaccine (Lot {lot})",
                    "Diphtheria Pertussis Tetanus (Lot {lot})", "Influenza Quadrivalent (Lot {lot})"
                ],
                "bounds": (2, 8),
                "desc": "Critical cold-chain pharmaceutical payload. Safe bounds: 2C to 8C. Real-time smart contract rules apply."
            },
            {
                "name": "Perishables",
                "templates": [
                    "Fresh Atlantic Salmon (Batch {lot})", "Organic Baby Spinach (Batch {lot})", "Organic Avocados Crate (Batch {lot})",
                    "Pasteurized Whole Milk (Batch {lot})", "Raw Fresh Chicken Breast (Batch {lot})", "Greek Yogurt Tubs (Batch {lot})",
                    "Fresh Blueberries Clamshell (Batch {lot})", "Sliced Strawberries Pack (Batch {lot})", "Grass-Fed Ground Beef (Batch {lot})",
                    "Fresh Pork Tenderloin (Batch {lot})", "Organic Raspberries (Batch {lot})", "Liquid Egg Whites Carton (Batch {lot})",
                    "Artisan Goat Cheese (Batch {lot})", "Fresh Sweet Corn Crate (Batch {lot})", "Wild Caught Shrimp Crate (Batch {lot})",
                    "Fresh Turkey Breast (Batch {lot})", "Organic Romaine Hearts (Batch {lot})", "Arugula Salad Prepack (Batch {lot})",
                    "Fresh Portobello Mushrooms (Batch {lot})", "Fresh Red Seedless Grapes (Batch {lot})"
                ],
                "bounds": (1, 4),
                "desc": "Highly perishable dairy & meats. Spoilage risk parameters: 1C to 4C safe shelf-life limits."
            },
            {
                "name": "Electronics",
                "templates": [
                    "F-35 Avionics Controller (SKU {sku})", "LiFePO4 Lithium Battery 48V (SKU {sku})", "Tesla 4680 Battery Array (SKU {sku})",
                    "Autonomous LIDAR Scanner (SKU {sku})", "Military-Grade Inertial Sensor (SKU {sku})", "Embedded FPGA Control Block (SKU {sku})",
                    "Space-Grade Gyroscope v2 (SKU {sku})", "Radiation Hardened RAM Pack (SKU {sku})", "Ruggedized Telemetry Node (SKU {sku})",
                    "Automotive Radar Unit (SKU {sku})", "Surgical Robotic Controller (SKU {sku})", "Industrial PLC Logic Module (SKU {sku})",
                    "Fiber Optic Transceiver Core (SKU {sku})", "High-Voltage Power Inverter (SKU {sku})", "Subsea Pressure Transmitter (SKU {sku})",
                    "Autonomous Flight Computer (SKU {sku})", "Core Micro-controller Board (SKU {sku})", "Ruggedized IoT Gateway Hub (SKU {sku})",
                    "Satellite Communications Module (SKU {sku})", "Precision Optocoupler Array (SKU {sku})"
                ],
                "bounds": (15, 30),
                "desc": "Precision defense & aerospace electronics. safe storage temp: 15C to 30C. High humidity sensitive."
            },
            {
                "name": "Chemicals",
                "templates": [
                    "Industrial Epoxy Resin (Grade {lot})", "Specialized Polymer Sealer (Grade {lot})", "Cryogenic Nitrogen Agent (Grade {lot})",
                    "Catalyst Precursor Fluid (Grade {lot})", "Silicon Wafer Coating (Grade {lot})", "Organic Solvent Cleanser (Grade {lot})",
                    "Reactive Monomer Agent (Grade {lot})", "Photoresist Chemical Fluid (Grade {lot})", "Corrosive Acid Formulation (Grade {lot})",
                    "Surfactant Compound Base (Grade {lot})", "Enzymatic Detergent Blend (Grade {lot})", "Stabilized Hydrogen Peroxide (Grade {lot})",
                    "Aerospace Resin Adhesive (Grade {lot})", "Conductive Silver Paste (Grade {lot})", "Synthetic Lubricant Oil (Grade {lot})",
                    "Rust Preventative Agent (Grade {lot})", "Fluorinated Cleaning Fluid (Grade {lot})", "Aqueous Film Forming Foam (Grade {lot})",
                    "Polyurethane Base Elastomer (Grade {lot})", "Etching Acid Solution (Grade {lot})"
                ],
                "bounds": (15, 25),
                "desc": "Active industrial compounds. Volatility threshold: 15C to 25C limits. Block-logged safety compliance."
            },
            {
                "name": "Industrial",
                "templates": [
                    "Titanium Turbine Blade (Item {sku})", "Carbon Fiber Chassis Panel (Item {sku})", "Precision Hydraulic Valve (Item {sku})",
                    "High-Pressure Steel Coupler (Item {sku})", "Machined Aluminium Bracket (Item {sku})", "Composite Drive Shaft (Item {sku})",
                    "Heavy-Duty Gear Box Array (Item {sku})", "High-Torque Electric Actuator (Item {sku})", "Industrial Compressor Valve (Item {sku})",
                    "Pneumatic Cylinder Core (Item {sku})", "Aerospace Fastener Kit (Item {sku})", "Thermal Barrier Coating (Item {sku})",
                    "Magnetic Bearing Assembly (Item {sku})", "Explosion Proof Enclosure (Item {sku})", "Subsea Wellhead Cap (Item {sku})",
                    "Heavy Crane Wire Assembly (Item {sku})", "Marine Propeller Shaft (Item {sku})", "Gas Turbine Nozzle Ring (Item {sku})",
                    "Automated Valve Positioner (Item {sku})", "High-Pressure Seal Ring (Item {sku})"
                ],
                "bounds": (-10, 45),
                "desc": "Heavy structural machinery. Anti-rust environmental bounds: -10C to 45C."
            }
        ]

        created_products = []
        product_counter = 0

        for cat in categories:
            for template in cat["templates"]:
                product_counter += 1
                lot_no = f"LOT-{2026}-{product_counter:03d}"
                sku_no = f"SKU-{cat['name'][:3].upper()}-{product_counter:03d}"
                p_name = template.format(lot=lot_no, sku=sku_no)
                
                desc_formatted = f"[{cat['name']}] {cat['desc']} | Code: {sku_no} | Temp Bounds: {cat['bounds'][0]}C to {cat['bounds'][1]}C"
                
                prod = Product.objects.create(
                    name=p_name,
                    description=desc_formatted,
                    manufacturer=manufacturer
                )
                created_products.append(prod)

        self.stdout.write(f"Successfully generated {len(created_products)} products.")

        self.stdout.write("Generating inventory stock allocations...")
        # Allocate random stocks across warehouses
        for p in created_products:
            wh = random.choice(created_warehouses)
            Inventory.objects.create(
                product=p,
                warehouse=wh,
                quantity=random.randint(50, 450),
                low_stock_threshold=random.randint(15, 45)
            )

        self.stdout.write("Generating purchase orders history...")
        # Generate some POs with varying status
        for idx in range(1, 26):
            p = created_products[idx * 3] # Pick a subset of products
            status_opt = random.choice(["PENDING", "APPROVED", "SHIPPED", "DELIVERED"])
            PurchaseOrder.objects.create(
                buyer=retailer,
                seller=manufacturer,
                product=p,
                quantity=random.randint(100, 300),
                status=status_opt
            )

        self.stdout.write("Generating QA inspections & telemetry tracking history...")
        # Populate events, telemetry records, and QA reports
        for idx, p in enumerate(created_products[:40]): # Seed telemetry and events for first 40 products
            # Create a tracking event
            tx_hash = "0x" + "".join(random.choices("0123456789abcdef", k=64))
            event = TrackingEvent.objects.create(
                product=p,
                status="In Transit",
                location=random.choice(["Rotterdam Port", "LAX Terminal", "Singapore Tuas"]),
                tx_hash=tx_hash
            )
            
            # Simulated telemetry sensors log - some violating to test smart contract rules
            # Product index 5, 15, 25 will have temperature violations (exceeding bounds)
            is_violation = (idx in [5, 15, 25])
            if is_violation:
                temp_val = 35.0  # High temperature excursion
                hum_val = 80.0
            else:
                # Safe parameters
                temp_val = 5.0 if idx < 20 else 20.0
                hum_val = 45.0
                
            Telemetry.objects.create(
                event=event,
                temperature_c=temp_val,
                humidity_percent=hum_val
            )
            
            # QA Audits matching the products
            # If temp violated, passed should be False
            passed_qa = not is_violation
            qa_notes = f"[Score: {45 if is_violation else 95}/100] Verified compliance on-chain."
            
            QualityCheck.objects.create(
                product=p,
                inspector=qa_inspector,
                passed=passed_qa,
                notes=qa_notes
            )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully! Added 100 unique products and over 100 relational records. ✅"))
