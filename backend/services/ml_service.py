import tensorflow as tf
import numpy as np
import io
import os
from PIL import Image
from ultralytics import YOLO
import cv2
import base64
from config import Config

class MLService:
    def __init__(self):
        self.model = None
        self.yolo_model = None
        self._model_loaded = False
        self._yolo_loaded = False
        self.output_class = ["Batteries", "Clothes", "E-waste", "Glass", "Light Bulbs", "Metal", "Organic", "Paper", "Plastic"]
        self.realtime_class_labels = ["Batteries", "Clothes", "E-waste", "Glass", "Light Bulbs", "Metal", "Organic", "Paper", "Plastic"]
        self.data = {
            "Batteries": [
                "Battery recycling is a recycling activity that aims to reduce the number of batteries being disposed as municipal solid waste. Batteries contain a number of heavy metals and toxic chemicals and disposing of them by the same process as regular household waste has raised concerns over soil contamination and water pollution.<br><br> Most types of batteries can be recycled. However, some batteries are recycled more readily than others, such as lead–acid automotive batteries (nearly 90% are recycled) and button cells (because of the value and toxicity of their chemicals). Rechargeable nickel–cadmium (Ni-Cd), nickel metal hydride (Ni-MH), lithium-ion (Li-ion) and nickel–zinc (Ni-Zn), can also be recycled. There is currently no cost-neutral recycling option available for disposable alkaline batteries, though consumer disposal guidelines vary by region.",
                "4XOAGNzWvqY", "oKFOqMZmuA8"
            ],
            "Clothes": [
                "Textile recycling is the process of recovering fiber, yarn or fabric and reprocessing the textile material into useful products. Textile waste products are gathered from different sources and are then sorted and processed depending on their condition, composition, and resale value. The end result of this processing can vary, from the production of energy and chemicals to new articles of clothing.<br><br>Due to a recent trend of over consumption and waste generation in global fashion culture, textile recycling has become a key focus of worldwide sustainability efforts. Globalization has led to a \"fast fashion\" trend where clothes are considered by many consumers to be disposable due to their increasingly lower prices. The development of recycled technology has allowed the textile industry to produce vast amounts of products that deplete natural resources.",
                "Bhi7S06pwv4", "IHPBJySIXZw"
            ],
            "E-waste": [
                "Electronic waste or e-waste describes discarded electrical or electronic devices. Used electronics which are destined for refurbishment, reuse, resale, salvage recycling through material recovery, or disposal are also considered e-waste. Informal processing of e-waste in developing countries can lead to adverse human health effects and environmental pollution.<br><br>Electronic scrap components, such as CPUs, contain potentially harmful materials such as lead, cadmium, beryllium, or brominated flame retardants. Recycling and disposal of e-waste may involve significant risk to health of workers and their communities.<br><br>E-waste or electronic waste is created when an electronic product is discarded after the end of its useful life. The rapid expansion of technology and the consumption driven society results in the creation of a very large amount of e-waste in every minute.",
                "aUwFXDLOFO0","w0ikFMTuS9c"
            ],
            "Glass": [
                "Glass recycling is the processing of waste glass into usable products. Glass that is crushed and ready to be remelted is called cullet. There are two types of cullet: internal and external. Internal cullet is composed of defective products detected and rejected by a quality control process during the industrial process of glass manufacturing, transition phases of product changes (such as thickness and colour changes) and production offcuts. External cullet is waste glass that has been collected or reprocessed with the purpose of recycling. External cullet (which can be pre- or post-consumer) is classified as waste. The word \"cullet\", when used in the context of end-of-waste, will always refer to external cullet.<br><br>To be recycled, glass waste needs to be purified and cleaned of contamination. Then, depending on the end use and local processing capabilities, it might also have to be separated into different colors. Many recyclers collect different colors of glass separately since glass retains its color after recycling.",
                "bYVih298o1Y", "6R8YObQbE88"
            ],
            "Light Bulbs": [
                "Recycling prevents the release of hazardous materials into the environment. Mercury, an extremely toxic heavy metal, is used in fluorescent light bulbs to increase energy efficiency. In addition to mercury, some HID bulbs contain radioactive substances like Krypton-85 and thorium used for quick and easy light ignition.<br><br>LEDs on the other hand do not contain mercury; but, they do contain nickel, lead, and trace amounts of arsenic. Light bulbs often break when thrown into a dumpster, trash can or compactor, or when they end up in a landfill or incinerator. This causes the release of hazardous materials into the environment and can create serious public and environmental health concerns.<br><br>It's also important to remember that recycling allows the reuse of the glass, metals and other materials that make up light bulbs. Virtually all components of light bulbs can be recycled.",
                "GbE9C2tTW2k", "PkfX4sZwrQ4"
            ],
            "Metal": [
                "Several kinds and also large amounts of metals are used in industrial processes every day. Since the industrial revolution period has taken place, our consumption levels skyrocketed due to the mass production of goods and the resulting low unit price.<br><br>The most consumed metal worldwide is aluminum, followed by copper, zinc, lead and nickel. Moreover, some precious materials like gold are used for our computers and other electronic devices.<br><br>Metal is therefore crucial to sustaining our living standard. However, metals are resources that are limited. The depletion of metals can be a big issue in the future since the world population grows rapidly and thus also the demand for goods made out of metal will increase.<br><br>To mitigate the problem of metal depletion, we have to look out for effective measures. One of those measures could be metal recycling.",
                "qAGCI0-pQ3E", "rgEEXhbar3A"
            ],
            "Organic": [
                "Organic wastes contain materials which originated from living organisms. There are many types of organic wastes and they can be found in municipal solid waste , industrial solid waste , agricultural waste, and wastewaters. Organic wastes are often disposed of with other wastes in landfills or incinerators, but since they are biodegradable , some organic wastes are suitable for composting and land application.<br><br>Organic materials found in municipal solid waste include food, paper, wood, sewage sludge , and yard waste. Because of recent shortages in landfill capacity, the number of municipal composting sites for yard wastes is increasing across the country, as is the number of citizens who compost yard wastes in their backyards. On a more limited basis, some mixed municipal waste composting is also taking place. In these systems, attempts to remove inorganic materials are made prior to composting.<br><br>Food waste from restaurants and grocery stores is typically disposed of through garbage disposals, therefore, it becomes a component of wastewater and sewage sludge.",
                "lHyL41grGUo", "2I8Tjb4Fy-Q"
            ],
            "Paper": [
                "The recycling of paper is the process by which waste paper is turned into new paper products. It has a number of important benefits: It saves waste paper from occupying homes of people and producing methane as it breaks down. Because paper fibre contains carbon (originally absorbed by the tree from which it was produced), recycling keeps the carbon locked up for longer and out of the atmosphere. Around two-thirds of all paper products in the US are now recovered and recycled, although it does not all become new paper. After repeated processing the fibres become too short for the production of new paper - this is why virgin fibre (from sustainably farmed trees) is frequently added to the pulp recipe.<br><br>Paper recycling pertains to the processes of reprocessing waste paper for reuse. Waste papers are either obtained from paper mill paper scraps, discarded paper materials, and waste paper material discarded after consumer use. Examples of the commonly known papers recycled are old newspapers and magazines.",
                "jAqVxsEgWIM", "xhW0RTg8kRI"
            ],
            "Plastic": [
                "Plastic recycling is the process of recovering scrap or waste plastic and reprocessing the material into useful products. Due to purposefully misleading symbols on plastic packaging and numerous technical hurdles, less than 10% of plastic has ever been recycled. Compared with the lucrative recycling of metal, and similar to the low value of glass recycling, plastic polymers recycling is often more challenging because of low density and low value.<br><br>Materials recovery facilities are responsible for sorting and processing plastics. As of 2019, due to limitations in their economic viability, these facilities have struggled to make a meaningful contribution to the plastic supply chain. The plastics industry has known since at least the 1970s that recycling of most plastics is unlikely because of these limitations. However, the industry has lobbied for the expansion of recycling while these companies have continued to increase the amount of virgin plastic being produced.",
                "rYwBL_6hB2I", "I_fUpP-hq3A"
            ]
        }
        # Load only TensorFlow model at startup, keep YOLO lazy-loaded
        self.load_tensorflow_model()
    
    def load_tensorflow_model(self):
        """Load only TensorFlow model at startup"""
        try:
            # If model is already loaded, return True
            if self.model is not None and self._model_loaded:
                return True
                
            # Unload YOLO model first if it's loaded
            self._unload_yolo_model()
            
            # Set environment variables for TensorFlow
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU usage
            os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
            
            # Clear any existing TensorFlow session
            import tensorflow as tf
            tf.keras.backend.clear_session()
            
            # Load the model
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            waste_model_path = os.path.join(backend_dir, 'ml_models', 'classifyWaste.h5')
            
            if os.path.exists(waste_model_path):
                self.model = tf.keras.models.load_model(waste_model_path, compile=False)
                self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
                self._model_loaded = True
                print("TensorFlow model loaded successfully")
                return True
            else:
                print(f"Error: Waste model not found at {waste_model_path}")
                self.model = None
                return False
                
        except Exception as e:
            print(f"Error loading TensorFlow model: {e}")
            self.model = None
            self._model_loaded = False
            return False
    
    def _load_yolo_model(self):
        """Lazy load YOLO model when needed"""
        try:
            # Unload TensorFlow model first if it's loaded
            self._unload_tensorflow_model()
            
            if self._yolo_loaded and self.yolo_model is not None:
                return True
                
            import gc
            import tensorflow as tf
            gc.collect()
            tf.keras.backend.clear_session()
            
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            yolo_model_path = os.path.join(backend_dir, 'ml_models', 'YOLO', 'streamlit-detection-tracking - app', 'weights', 'yoloooo.pt')
            
            if os.path.exists(yolo_model_path):
                # Set environment variables for YOLO
                os.environ['YOLO_VERBOSE'] = 'False'
                os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU for YOLO
                
                self.yolo_model = YOLO(yolo_model_path)
                self._yolo_loaded = True
                print("YOLO model loaded successfully")
                return True
            else:
                print(f"Warning: YOLO model not found at {yolo_model_path}")
                self.yolo_model = None
                return False
                
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.yolo_model = None
            self._yolo_loaded = False
            return False
    
    def _unload_yolo_model(self):
        """Safely unload YOLO model and clean up"""
        if hasattr(self, 'yolo_model') and self.yolo_model is not None:
            try:
                del self.yolo_model
                self.yolo_model = None
                self._yolo_loaded = False
                import gc
                gc.collect()
                print("YOLO model unloaded successfully")
                return True
            except Exception as e:
                print(f"Error unloading YOLO model: {e}")
                return False
        return True

    def _unload_tensorflow_model(self):
        """Safely unload TensorFlow model and clean up"""
        if hasattr(self, 'model') and self.model is not None:
            try:
                import tensorflow as tf
                tf.keras.backend.clear_session()
                del self.model
                self.model = None
                import gc
                gc.collect()
                print("TensorFlow model unloaded successfully")
                return True
            except Exception as e:
                print(f"Error unloading TensorFlow model: {e}")
                return False
        return True

    def _ensure_tensorflow_loaded(self):
        """Ensure TensorFlow model is loaded and YOLO is unloaded"""
        if self._yolo_loaded:
            self._unload_yolo_model()
        
        if self.model is None:
            self.load_tensorflow_model()
        
        return self.model is not None

    def _ensure_yolo_loaded(self):
        """Ensure YOLO model is loaded and TensorFlow is unloaded"""
        if not self._yolo_loaded:
            if self.model is not None:
                self._unload_tensorflow_model()
            self._load_yolo_model()
        
        return self._yolo_loaded and self.yolo_model is not None

    def classify_waste(self, image_path):
        """Classify waste from image path"""
        if not self._ensure_tensorflow_loaded():
            return "Error", "Failed to load TensorFlow model", "", ""
        
        test_image = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        test_image = tf.keras.preprocessing.image.img_to_array(test_image) / 255
        test_image = np.expand_dims(test_image, axis=0)
        predicted_array = self.model.predict(test_image)
        predicted_value = self.output_class[np.argmax(predicted_array)]
        return predicted_value, self.data[predicted_value][0], self.data[predicted_value][1], self.data[predicted_value][2]
    
    def classify_waste_bytes(self, img_bytes):
        """Classify waste from image bytes"""
        if not self._ensure_tensorflow_loaded():
            return "Error"
        
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img = img.resize((224, 224))
        arr = np.array(img).astype('float32') / 255.0
        arr = np.expand_dims(arr, axis=0)
        preds = self.model.predict(arr, verbose=0)
        pred_idx = int(np.argmax(preds[0]))
        return self.output_class[pred_idx]
    
    def realtime_predict(self, img_data):
        """Real-time prediction from base64 image data"""
        try:
            if not self._ensure_tensorflow_loaded():
                return {'label': 'Model not available', 'confidence': ''}
            
            if ',' in img_data:
                img_data = img_data.split(',')[1]
            
            img_bytes = base64.b64decode(img_data)
            img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            img = img.resize((224, 224))
            arr = np.array(img).astype('float32') / 255.0
            arr = np.expand_dims(arr, axis=0)
            preds = self.model.predict(arr, verbose=0)
            pred_idx = int(np.argmax(preds[0]))
            confidence = float(preds[0][pred_idx])
            label = self.realtime_class_labels[pred_idx] if pred_idx < len(self.realtime_class_labels) else 'Unknown'
            return {'label': label, 'confidence': f'{confidence:.2f}'}
        except Exception as e:
            return {'label': 'Error', 'confidence': ''}
    
    def process_multi_waste_image(self, image_data):
        """Process image using YOLOv8 for multi-waste detection"""
        try:
            # Ensure YOLO model is loaded and TensorFlow is unloaded
            if not self._ensure_yolo_loaded():
                return {
                    'success': False, 
                    'error': 'Failed to load YOLO model. Please try again.'
                }
            
            if isinstance(image_data, str):
                img = cv2.imread(image_data)
            else:
                # Reset file pointer to beginning
                image_data.seek(0)
                nparr = np.frombuffer(image_data.read(), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {'success': False, 'error': 'Could not decode image'}

            results = self.yolo_model(img)
            
            detections = []
            for r in results:
                boxes = r.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        class_name = self.yolo_model.names[cls]
                        
                        detections.append({
                            'class': class_name,
                            'confidence': conf,
                            'bbox': [int(x1), int(y1), int(x2), int(y2)]
                        })
                        
                        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.putText(img, f"{class_name} {conf:.2f}", (int(x1), int(y1) - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            _, buffer = cv2.imencode('.jpg', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'success': True,
                'image_url': f"data:image/jpeg;base64,{img_base64}",
                'detections': detections
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
