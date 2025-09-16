#!/usr/bin/env python3
"""
College Timetable Generator using Google OR-Tools CP-SAT Solver
This script generates optimized weekly timetables for two divisions (TY_A and TY_B)
with proper constraint handling as specified in project requirements.
"""

from ortools.sat.python import cp_model
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Any

class TimetableGenerator:
    def __init__(self):
        # Fixed time structure
        self.time_slots = [
            "10:30-11:30", "11:30-12:30", "12:30-1:30", 
            "2:00-3:00", "3:00-4:00", "4:00-5:00", "5:00-6:00"
        ]
        # Note: 1:30-2:00 is a break and not a schedulable slot
        self.schedulable_slots = [0, 1, 2, 3, 4, 5, 6]  # All slots except break
        self.break_slot_index = None  # We'll handle break properly in constraints
        
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.divisions = ["TY_A", "TY_B"]
        self.batches = ["P", "Q", "R"]  # For practical sessions
        self.lab_capacity = 1  # Each lab can host one batch at a time
        
        # User input data
        self.subjects = {}
        self.teachers = {}
        self.labs = []
        self.subject_teacher_mapping = {}
        
        # OR-Tools model
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        # Decision variables
        self.schedule_vars = {}
        self.teacher_schedule = {}
        
    def get_user_input(self):
        """Get all timetable requirements from user"""
        
        print("=" * 60)
        print("COLLEGE TIMETABLE GENERATOR")
        print("=" * 60)
        
        # Get practical labs
        self.get_labs_input()
        
        # Get subjects
        self.get_subjects_input()
        
        # Get teachers
        self.get_teachers_input()
        
        # Assign teachers to subjects
        self.assign_teachers_to_subjects()
        
        print("\n" + "=" * 60)
        print("INPUT SUMMARY:")
        self.display_input_summary()
        
        confirm = input("\nProceed with timetable generation? (y/n): ").lower()
        if confirm != 'y':
            print("Exiting...")
            return False
        return True
    
    def get_labs_input(self):
        """Get practical lab information"""
        print("\n--- PRACTICAL LABS SETUP ---")
        
        while True:
            try:
                num_labs = int(input("Enter number of practical labs available: "))
                if num_labs > 0:
                    break
                else:
                    print("Number of labs must be positive!")
            except ValueError:
                print("Please enter a valid number!")
        
        for i in range(num_labs):
            while True:
                lab_name = input(f"Enter name for lab {i+1}: ").strip()
                if lab_name and lab_name not in self.labs:
                    self.labs.append(lab_name)
                    break
                elif not lab_name:
                    print("Lab name cannot be empty!")
                else:
                    print("Lab name already exists!")
    
    def get_subjects_input(self):
        """Get subject information from user - each subject must have both theory and practical"""
        print("\n--- SUBJECTS SETUP ---")
        print("Note: Each subject must have both theory and practical components")
        
        while True:
            try:
                num_subjects = int(input("Enter number of subjects: "))
                if num_subjects > 0:
                    break
                else:
                    print("Number of subjects must be positive!")
            except ValueError:
                print("Please enter a valid number!")
        
        for i in range(num_subjects):
            print(f"\n--- Subject {i+1} ---")
            
            # Subject name
            while True:
                subject_name = input("Enter subject name: ").strip().upper()
                if subject_name and subject_name not in self.subjects:
                    break
                elif not subject_name:
                    print("Subject name cannot be empty!")
                else:
                    print("Subject already exists!")
            
            subject_info = {"type": "both"}  # All subjects must have both theory and practical
            
            # Get theory hours
            while True:
                try:
                    theory_lectures = int(input("Enter minimum theory lectures per week: "))
                    if theory_lectures > 0:
                        subject_info["theory_per_week"] = theory_lectures
                        break
                    else:
                        print("Number of lectures must be positive!")
                except ValueError:
                    print("Please enter a valid number!")
            
            # Get practical hours
            while True:
                try:
                    practical_lectures = int(input("Enter minimum practical lectures per week: "))
                    if practical_lectures > 0:
                        subject_info["practical_per_week"] = practical_lectures
                        break
                    else:
                        print("Number of lectures must be positive!")
                except ValueError:
                    print("Please enter a valid number!")
            
            # Get preferred labs for practical sessions
            if self.labs:
                print(f"Available labs: {', '.join(self.labs)}")
                preferred_labs = []
                while True:
                    lab_input = input("Enter preferred labs for practicals (comma-separated, or 'all' for all labs): ").strip()
                    if lab_input.lower() == 'all':
                        preferred_labs = self.labs.copy()
                        break
                    else:
                        labs_list = [lab.strip() for lab in lab_input.split(',')]
                        valid_labs = [lab for lab in labs_list if lab in self.labs]
                        if valid_labs:
                            preferred_labs = valid_labs
                            break
                        else:
                            print("Please enter valid lab names!")
                
                subject_info["preferred_labs"] = preferred_labs
            else:
                subject_info["preferred_labs"] = []
            
            self.subjects[subject_name] = subject_info
    
    def get_teachers_input(self):
        """Get teacher information from user"""
        print("\n--- TEACHERS SETUP ---")
        
        while True:
            try:
                num_teachers = int(input("Enter number of teachers: "))
                if num_teachers > 0:
                    break
                else:
                    print("Number of teachers must be positive!")
            except ValueError:
                print("Please enter a valid number!")
        
        for i in range(num_teachers):
            print(f"\n--- Teacher {i+1} ---")
            
            # Teacher ID
            while True:
                teacher_id = input("Enter teacher ID: ").strip().upper()
                if teacher_id and teacher_id not in self.teachers:
                    break
                elif not teacher_id:
                    print("Teacher ID cannot be empty!")
                else:
                    print("Teacher ID already exists!")
            
            # Teacher name
            teacher_name = input("Enter teacher name: ").strip()
            if not teacher_name:
                teacher_name = f"Teacher_{teacher_id}"
            
            # Subjects taught by this teacher
            print(f"Available subjects: {', '.join(self.subjects.keys())}")
            while True:
                subjects_input = input("Enter subjects taught by this teacher (comma-separated): ").strip()
                subjects_list = [subj.strip().upper() for subj in subjects_input.split(',')]
                valid_subjects = [subj for subj in subjects_list if subj in self.subjects]
                
                if valid_subjects:
                    self.teachers[teacher_id] = {
                        "name": teacher_name,
                        "subjects": valid_subjects
                    }
                    break
                else:
                    print("Please enter valid subject names!")
    
    def assign_teachers_to_subjects(self):
        """Create subject-teacher mapping and handle conflicts"""
        print("\n--- TEACHER-SUBJECT ASSIGNMENT ---")
        
        # Check for subjects without teachers
        unassigned_subjects = []
        for subject in self.subjects:
            assigned = False
            for teacher_id, teacher_info in self.teachers.items():
                if subject in teacher_info["subjects"]:
                    if subject not in self.subject_teacher_mapping:
                        self.subject_teacher_mapping[subject] = teacher_id
                        assigned = True
                    else:
                        # Multiple teachers for same subject - ask user to choose
                        print(f"\nMultiple teachers available for {subject}:")
                        print(f"Current: {self.teachers[self.subject_teacher_mapping[subject]]['name']} ({self.subject_teacher_mapping[subject]})")
                        print(f"Alternative: {teacher_info['name']} ({teacher_id})")
                        
                        while True:
                            choice = input(f"Choose teacher for {subject} (1 for current, 2 for alternative): ").strip()
                            if choice == "1":
                                break
                            elif choice == "2":
                                self.subject_teacher_mapping[subject] = teacher_id
                                break
                            else:
                                print("Please enter 1 or 2!")
                        assigned = True
            
            if not assigned:
                unassigned_subjects.append(subject)
        
        # Handle unassigned subjects
        if unassigned_subjects:
            print(f"\nWarning: The following subjects have no assigned teachers: {', '.join(unassigned_subjects)}")
            print("Please assign teachers to these subjects:")
            
            for subject in unassigned_subjects:
                print(f"\nAvailable teachers:")
                for i, (teacher_id, teacher_info) in enumerate(self.teachers.items(), 1):
                    print(f"{i}. {teacher_info['name']} ({teacher_id})")
                
                while True:
                    try:
                        choice = int(input(f"Choose teacher for {subject} (enter number): "))
                        teacher_list = list(self.teachers.keys())
                        if 1 <= choice <= len(teacher_list):
                            chosen_teacher = teacher_list[choice - 1]
                            self.subject_teacher_mapping[subject] = chosen_teacher
                            # Add subject to teacher's list
                            self.teachers[chosen_teacher]["subjects"].append(subject)
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(teacher_list)}!")
                    except ValueError:
                        print("Please enter a valid number!")
    
    def display_input_summary(self):
        """Display summary of all input data"""
        print(f"Labs: {', '.join(self.labs)}")
        print(f"Divisions: {', '.join(self.divisions)}")
        print(f"Days: {', '.join(self.days)}")
        print(f"Time Slots: {', '.join(self.time_slots)}")
        print("(Note: 1:30-2:00 is a break and not a schedulable slot)")
        
        print("\nSubjects:")
        for subject, info in self.subjects.items():
            print(f"  {subject}: {info}")
        
        print("\nTeachers:")
        for teacher_id, info in self.teachers.items():
            print(f"  {teacher_id}: {info}")
        
        print("\nSubject-Teacher Assignments:")
        for subject, teacher_id in self.subject_teacher_mapping.items():
            teacher_name = self.teachers[teacher_id]['name']
            print(f"  {subject} -> {teacher_name} ({teacher_id})")
    
    def create_decision_variables(self):
        """Create decision variables for the timetable"""
        
        # Schedule variables: [day][slot][division][subject][session_type][batch][lab]
        for day_idx in range(len(self.days)):
            self.schedule_vars[day_idx] = {}
            for slot_idx in range(len(self.time_slots)):
                self.schedule_vars[day_idx][slot_idx] = {}
                for div_idx in range(len(self.divisions)):
                    self.schedule_vars[day_idx][slot_idx][div_idx] = {}
                    for subject in self.subjects:
                        self.schedule_vars[day_idx][slot_idx][div_idx][subject] = {}
                        
                        # Theory sessions (if subject has theory)
                        if self.subjects[subject]["theory_per_week"] > 0:
                            self.schedule_vars[day_idx][slot_idx][div_idx][subject]["theory"] = \
                                self.model.NewBoolVar(f"schedule_{day_idx}_{slot_idx}_{div_idx}_{subject}_theory")
                        
                        # Practical sessions (if subject has practical)
                        if self.subjects[subject]["practical_per_week"] > 0:
                            self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"] = {}
                            for batch in self.batches:
                                self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch] = {}
                                # Only use labs that are preferred for this subject
                                preferred_labs = self.subjects[subject].get("preferred_labs", self.labs)
                                for lab in preferred_labs:
                                    self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch][lab] = \
                                        self.model.NewBoolVar(f"schedule_{day_idx}_{slot_idx}_{div_idx}_{subject}_practical_{batch}_{lab}")
        
        # Teacher schedule variables
        for day_idx in range(len(self.days)):
            self.teacher_schedule[day_idx] = {}
            for slot_idx in range(len(self.time_slots)):
                self.teacher_schedule[day_idx][slot_idx] = {}
                for teacher_id in self.teachers:
                    self.teacher_schedule[day_idx][slot_idx][teacher_id] = \
                        self.model.NewBoolVar(f"teacher_{teacher_id}_{day_idx}_{slot_idx}")
    
    def add_constraints(self):
        """Add all timetable constraints"""
        
        # 1. Each slot can have at most one activity per division
        for day_idx in range(len(self.days)):
            for slot_idx in range(len(self.time_slots)):
                for div_idx in range(len(self.divisions)):
                    slot_activities = []
                    
                    for subject in self.subjects:
                        # Theory activity
                        if "theory" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                            slot_activities.append(
                                self.schedule_vars[day_idx][slot_idx][div_idx][subject]["theory"]
                            )
                        
                        # Practical activities
                        if "practical" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                            for batch in self.batches:
                                for lab in self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch]:
                                    slot_activities.append(
                                        self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch][lab]
                                    )
                    
                    if slot_activities:
                        self.model.Add(sum(slot_activities) <= 1)
        
        # 2. Minimum lectures per week for each subject
        for subject, requirements in self.subjects.items():
            for div_idx in range(len(self.divisions)):
                # Theory lectures
                if requirements["theory_per_week"] > 0:
                    theory_lectures = []
                    for day_idx in range(len(self.days)):
                        for slot_idx in range(len(self.time_slots)):
                            if "theory" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                                theory_lectures.append(
                                    self.schedule_vars[day_idx][slot_idx][div_idx][subject]["theory"]
                                )
                    
                    if theory_lectures:
                        self.model.Add(sum(theory_lectures) >= requirements["theory_per_week"])
                
                # Practical lectures
                if requirements["practical_per_week"] > 0:
                    practical_lectures = []
                    for day_idx in range(len(self.days)):
                        for slot_idx in range(len(self.time_slots)):
                            if "practical" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                                # Count practical as scheduled if any batch is assigned
                                practical_vars_in_slot = []
                                for batch in self.batches:
                                    for lab in self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch]:
                                        practical_vars_in_slot.append(
                                            self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch][lab]
                                        )
                                
                                if practical_vars_in_slot:
                                    # Create indicator variable for practical in this slot
                                    practical_indicator = self.model.NewBoolVar(f"practical_indicator_{subject}_{div_idx}_{day_idx}_{slot_idx}")
                                    self.model.Add(sum(practical_vars_in_slot) >= 1).OnlyEnforceIf(practical_indicator)
                                    self.model.Add(sum(practical_vars_in_slot) == 0).OnlyEnforceIf(practical_indicator.Not())
                                    practical_lectures.append(practical_indicator)
                    
                    if practical_lectures:
                        self.model.Add(sum(practical_lectures) >= requirements["practical_per_week"])
        
        # 3. Mutual exclusion: If Division A has practical, Division B must have theory (and vice versa)
        for day_idx in range(len(self.days)):
            for slot_idx in range(len(self.time_slots)):
                # Create boolean variables for whether each division has practical/theory in this slot
                div_a_has_practical = self.model.NewBoolVar(f"div_a_has_practical_{day_idx}_{slot_idx}")
                div_b_has_practical = self.model.NewBoolVar(f"div_b_has_practical_{day_idx}_{slot_idx}")
                div_a_has_theory = self.model.NewBoolVar(f"div_a_has_theory_{day_idx}_{slot_idx}")
                div_b_has_theory = self.model.NewBoolVar(f"div_b_has_theory_{day_idx}_{slot_idx}")
                
                # Collect all practical and theory variables for each division
                div_a_practical_vars = []
                div_b_practical_vars = []
                div_a_theory_vars = []
                div_b_theory_vars = []
                
                for subject in self.subjects:
                    # Division A
                    if "practical" in self.schedule_vars[day_idx][slot_idx][0][subject]:
                        for batch in self.batches:
                            for lab in self.schedule_vars[day_idx][slot_idx][0][subject]["practical"][batch]:
                                div_a_practical_vars.append(
                                    self.schedule_vars[day_idx][slot_idx][0][subject]["practical"][batch][lab]
                                )
                    
                    if "theory" in self.schedule_vars[day_idx][slot_idx][0][subject]:
                        div_a_theory_vars.append(
                            self.schedule_vars[day_idx][slot_idx][0][subject]["theory"]
                        )
                    
                    # Division B
                    if "practical" in self.schedule_vars[day_idx][slot_idx][1][subject]:
                        for batch in self.batches:
                            for lab in self.schedule_vars[day_idx][slot_idx][1][subject]["practical"][batch]:
                                div_b_practical_vars.append(
                                    self.schedule_vars[day_idx][slot_idx][1][subject]["practical"][batch][lab]
                                )
                    
                    if "theory" in self.schedule_vars[day_idx][slot_idx][1][subject]:
                        div_b_theory_vars.append(
                            self.schedule_vars[day_idx][slot_idx][1][subject]["theory"]
                        )
                
                # Link the boolean variables to the actual schedule variables
                if div_a_practical_vars:
                    self.model.Add(sum(div_a_practical_vars) >= 1).OnlyEnforceIf(div_a_has_practical)
                    self.model.Add(sum(div_a_practical_vars) == 0).OnlyEnforceIf(div_a_has_practical.Not())
                
                if div_b_practical_vars:
                    self.model.Add(sum(div_b_practical_vars) >= 1).OnlyEnforceIf(div_b_has_practical)
                    self.model.Add(sum(div_b_practical_vars) == 0).OnlyEnforceIf(div_b_has_practical.Not())
                
                if div_a_theory_vars:
                    self.model.Add(sum(div_a_theory_vars) >= 1).OnlyEnforceIf(div_a_has_theory)
                    self.model.Add(sum(div_a_theory_vars) == 0).OnlyEnforceIf(div_a_has_theory.Not())
                
                if div_b_theory_vars:
                    self.model.Add(sum(div_b_theory_vars) >= 1).OnlyEnforceIf(div_b_has_theory)
                    self.model.Add(sum(div_b_theory_vars) == 0).OnlyEnforceIf(div_b_has_theory.Not())
                
                # Implement the mutual exclusion constraint:
                # If Div A has practical → Div B must have theory
                # If Div B has practical → Div A must have theory
                self.model.AddImplication(div_a_has_practical, div_b_has_theory)
                self.model.AddImplication(div_b_has_practical, div_a_has_theory)
        
        # 4. Lab capacity constraint - each lab can host only one batch at a time
        for day_idx in range(len(self.days)):
            for slot_idx in range(len(self.time_slots)):
                for lab in self.labs:
                    lab_usage = []
                    for div_idx in range(len(self.divisions)):
                        for subject in self.subjects:
                            if "practical" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                                for batch in self.batches:
                                    if lab in self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch]:
                                        lab_usage.append(
                                            self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch][lab]
                                        )
                    
                    if lab_usage:
                        self.model.Add(sum(lab_usage) <= 1)
        
        # 5. Teacher constraints
        for day_idx in range(len(self.days)):
            for slot_idx in range(len(self.time_slots)):
                for teacher_id in self.teachers:
                    # Link teacher schedule with subject schedule
                    teacher_subjects_vars = []
                    
                    for subject in self.teachers[teacher_id]["subjects"]:
                        for div_idx in range(len(self.divisions)):
                            # Theory
                            if "theory" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                                teacher_subjects_vars.append(
                                    self.schedule_vars[day_idx][slot_idx][div_idx][subject]["theory"]
                                )
                            
                            # Practical
                            if "practical" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                                for batch in self.batches:
                                    for lab in self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch]:
                                        teacher_subjects_vars.append(
                                            self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch][lab]
                                        )
                    
                    if teacher_subjects_vars:
                        # Teacher is busy if any of their subjects are scheduled
                        for var in teacher_subjects_vars:
                            self.model.Add(
                                self.teacher_schedule[day_idx][slot_idx][teacher_id] >= var
                            )
                        
                        self.model.Add(
                            sum(teacher_subjects_vars) <= 
                            len(teacher_subjects_vars) * self.teacher_schedule[day_idx][slot_idx][teacher_id]
                        )
        
        # 6. Teacher consecutive lectures constraint (must have a break)
        for day_idx in range(len(self.days)):
            for teacher_id in self.teachers:
                for slot_idx in range(len(self.time_slots) - 1):
                    # Cannot have consecutive lectures
                    # Special handling for lunch break (slot 2 to slot 3: 12:30-1:30 to 2:00-3:00)
                    # We treat the break as a natural break, so we don't explicitly prevent
                    # consecutive lectures across the break
                    if slot_idx != 2:  # Don't constrain across lunch break
                        self.model.Add(
                            self.teacher_schedule[day_idx][slot_idx][teacher_id] +
                            self.teacher_schedule[day_idx][slot_idx + 1][teacher_id] <= 1
                        )
        
        # 7. For practical sessions, all 3 batches must be assigned to labs if practical is scheduled
        for day_idx in range(len(self.days)):
            for slot_idx in range(len(self.time_slots)):
                for div_idx in range(len(self.divisions)):
                    for subject in self.subjects:
                        if "practical" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                            # If any batch is scheduled, all batches must be scheduled too
                            batch_vars = []
                            for batch in self.batches:
                                batch_lab_vars = []
                                for lab in self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch]:
                                    batch_lab_vars.append(
                                        self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch][lab]
                                    )
                                
                                if batch_lab_vars:
                                    batch_var = self.model.NewBoolVar(f"batch_{batch}_scheduled_{day_idx}_{slot_idx}_{div_idx}_{subject}")
                                    batch_vars.append(batch_var)
                                    
                                    # Link batch_var to actual lab assignments
                                    self.model.Add(sum(batch_lab_vars) >= 1).OnlyEnforceIf(batch_var)
                                    self.model.Add(sum(batch_lab_vars) == 0).OnlyEnforceIf(batch_var.Not())
                            
                            # If we have any batch variables, ensure they're all equal
                            if len(batch_vars) > 1:
                                for i in range(1, len(batch_vars)):
                                    self.model.Add(batch_vars[0] == batch_vars[i])
    
    def solve_timetable(self):
        """Solve the timetable using CP-SAT solver"""
        print("\n" + "=" * 60)
        print("GENERATING TIMETABLE...")
        print("=" * 60)
        
        self.create_decision_variables()
        self.add_constraints()
        
        # Set solver parameters
        self.solver.parameters.max_time_in_seconds = 300  # 5 minutes timeout
        self.solver.parameters.enumerate_all_solutions = False
        
        # Solve
        status = self.solver.Solve(self.model)
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print("✅ Timetable generated successfully!")
            return True
        else:
            print("❌ Could not generate a valid timetable with given constraints.")
            print("Try reducing the number of required lectures or increasing available time slots.")
            return False
    
    def extract_solution(self):
        """Extract and format the solution"""
        timetable = {}
        
        for day_idx, day in enumerate(self.days):
            timetable[day] = {}
            for slot_idx, slot in enumerate(self.time_slots):
                timetable[day][slot] = {"TY_A": None, "TY_B": None}
                
                for div_idx, division in enumerate(self.divisions):
                    for subject in self.subjects:
                        # Check theory
                        if "theory" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                            if self.solver.Value(self.schedule_vars[day_idx][slot_idx][div_idx][subject]["theory"]):
                                teacher_id = self.subject_teacher_mapping[subject]
                                teacher_name = self.teachers[teacher_id]["name"]
                                timetable[day][slot][division] = {
                                    "subject": subject,
                                    "type": "Theory",
                                    "teacher": f"{teacher_name} ({teacher_id})",
                                    "lab": None,
                                    "batches": None
                                }
                        
                        # Check practical
                        if "practical" in self.schedule_vars[day_idx][slot_idx][div_idx][subject]:
                            practical_info = {}
                            for batch in self.batches:
                                for lab in self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch]:
                                    if self.solver.Value(self.schedule_vars[day_idx][slot_idx][div_idx][subject]["practical"][batch][lab]):
                                        if subject not in practical_info:
                                            practical_info[subject] = {}
                                        practical_info[subject][batch] = lab
                            
                            if practical_info:
                                subject_name = list(practical_info.keys())[0]
                                teacher_id = self.subject_teacher_mapping[subject_name]
                                teacher_name = self.teachers[teacher_id]["name"]
                                
                                batch_lab_info = []
                                for batch, lab in practical_info[subject_name].items():
                                    batch_lab_info.append(f"{batch}→{lab}")
                                
                                timetable[day][slot][division] = {
                                    "subject": subject_name,
                                    "type": "Practical",
                                    "teacher": f"{teacher_name} ({teacher_id})",
                                    "lab": ", ".join([info.split("→")[1] for info in batch_lab_info]),
                                    "batches": ", ".join(batch_lab_info)
                                }
        
        return timetable
    
    def display_timetable(self, timetable):
        """Display the timetable in a readable format"""
        print("\n" + "=" * 120)
        print("GENERATED TIMETABLE")
        print("=" * 120)
        
        for day in self.days:
            print(f"\n{day.upper()}")
            print("-" * 120)
            
            # Header
            print(f"{'Time':<15} {'TY Division A':<50} {'TY Division B':<50}")
            print("-" * 120)
            
            for slot_idx, slot in enumerate(self.time_slots):
                # Special handling for break time
                if slot_idx == 3 and slot == "2:00-3:00":  # After the break
                    print(f"{'1:30-2:00':<15} {'BREAK':<50} {'BREAK':<50}")
                
                div_a_info = timetable[day][slot]["TY_A"]
                div_b_info = timetable[day][slot]["TY_B"]
                
                div_a_text = "FREE" if not div_a_info else f"{div_a_info['subject']} ({div_a_info['type']}) - {div_a_info['teacher']}"
                div_b_text = "FREE" if not div_b_info else f"{div_b_info['subject']} ({div_b_info['type']}) - {div_b_info['teacher']}"
                
                if div_a_info and div_a_info['type'] == 'Practical':
                    div_a_text += f" | {div_a_info['batches']}"
                
                if div_b_info and div_b_info['type'] == 'Practical':
                    div_b_text += f" | {div_b_info['batches']}"
                
                print(f"{slot:<15} {div_a_text:<50} {div_b_text:<50}")
    
    def export_to_json(self, timetable):
        """Export timetable to JSON file"""
        filename = "college_timetable.json"
        with open(filename, 'w') as f:
            json.dump(timetable, f, indent=2)
        print(f"\n✅ Timetable exported to {filename}")
    
    def run(self):
        """Main execution function"""
        if not self.get_user_input():
            return
        
        if self.solve_timetable():
            timetable = self.extract_solution()
            self.display_timetable(timetable)
            
            # Ask user if they want to export
            export_choice = input("\nDo you want to export the timetable to JSON? (y/n): ").lower()
            if export_choice == 'y':
                self.export_to_json(timetable)
            
            self.display_statistics()
        else:
            self.suggest_modifications()
    
    def display_statistics(self):
        """Display timetable statistics"""
        print("\n" + "=" * 60)
        print("TIMETABLE STATISTICS")
        print("=" * 60)
        
        # Calculate utilization
        total_slots = len(self.days) * len(self.time_slots) * len(self.divisions)
        
        # Count teacher workload
        teacher_workload = {teacher_id: 0 for teacher_id in self.teachers}
        
        for day_idx in range(len(self.days)):
            for slot_idx in range(len(self.time_slots)):
                for teacher_id in self.teachers:
                    if self.solver.Value(self.teacher_schedule[day_idx][slot_idx][teacher_id]):
                        teacher_workload[teacher_id] += 1
        
        print("Teacher Workload:")
        for teacher_id, workload in teacher_workload.items():
            teacher_name = self.teachers[teacher_id]["name"]
            subjects = ", ".join(self.teachers[teacher_id]["subjects"])
            print(f"  {teacher_name} ({teacher_id}): {workload} slots | Subjects: {subjects}")
        
        # Lab utilization
        print(f"\nAvailable Labs: {', '.join(self.labs)}")
        print(f"Total Time Slots: {len(self.days)} days × {len(self.time_slots)} slots = {len(self.days) * len(self.time_slots)} slots per division")
    
    def suggest_modifications(self):
        """Suggest modifications if no solution found"""
        print("\n" + "=" * 60)
        print("SUGGESTIONS FOR MODIFICATION")
        print("=" * 60)
        
        total_theory_req = sum(subj["theory_per_week"] for subj in self.subjects.values())
        total_practical_req = sum(subj["practical_per_week"] for subj in self.subjects.values())
        
        available_slots = len(self.days) * len(self.time_slots)
        
        print(f"Total theory lectures required per division per week: {total_theory_req}")
        print(f"Total practical lectures required per division per week: {total_practical_req}")
        print(f"Available time slots per division per week: {available_slots}")
        
        if total_theory_req + total_practical_req > available_slots:
            print("\n⚠️  OVERLOADED SCHEDULE:")
            print("The total required lectures exceed available time slots.")
            print("Suggestions:")
            print("1. Reduce minimum lectures per week for some subjects")
            print("2. Add more time slots (extend college hours)")
            print("3. Consider alternate week schedules for some subjects")
        
        print("\n📋 Other suggestions:")
        print("1. Check if teacher assignments are realistic")
        print("2. Ensure sufficient practical labs are available")
        print("3. Review if consecutive lecture constraints are too restrictive")
        print("4. Consider reducing the number of practical batches")


def main():
    """Main function to run the timetable generator"""
    try:
        print("College Timetable Generator")
        print("This tool will help you create an optimized weekly timetable.")
        print("Please ensure you have the required libraries installed:")
        print("pip install ortools")
        print("\nPress Ctrl+C at any time to exit.\n")
        
        generator = TimetableGenerator()
        generator.run()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Goodbye!")
    except ImportError as e:
        print(f"\n❌ Error: Missing required library - {e}")
        print("Please install required libraries:")
        print("pip install ortools")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your input and try again.")


if __name__ == "__main__":
    main()